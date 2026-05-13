package com.hacker;

import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpHandler;
import com.sun.net.httpserver.HttpServer;

import java.io.File;
import java.io.IOException;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.nio.file.Files;
import java.sql.*;
import java.util.HashMap;
import java.util.Locale;
import java.util.Map;

public class Main {
    static Connection conn;
    static Map<Integer, TargetNode> targetsMap = new HashMap<>();

    public static void main(String[] args) throws Exception {
        System.out.println("[SYSTEM] Запуск протокола CT-OS...");
        
        String dbUrl = "jdbc:h2:./tomsk_hacker";
        File dbFile = new File("tomsk_hacker.mv.db");
        
        if (!dbFile.exists()) {
            System.err.println("[ERROR] БД не найдена!");
            return;
        }

        conn = DriverManager.getConnection(dbUrl, "sa", "");
        
        long startTime = System.currentTimeMillis();

        loadMapNodes();
        long endTime = System.currentTimeMillis();
        System.out.println(">>> ВРЕМЯ ЗАГРУЗКИ ДАННЫХ: " + (endTime - startTime) + " мс");


        HttpServer server = HttpServer.create(new InetSocketAddress(8080), 0);
        server.createContext("/", new FrontendHandler());
        server.createContext("/api/targets", new MapDataHandler());
        server.createContext("/api/load", new LoadDataHandler());
        server.createContext("/api/hack", new HackDataHandler());
        server.start();
        server.createContext("/photos/", new PhotoFileHandler());
        server.createContext("/api/steal", new StealMoneyHandler());
        System.out.println("[SYSTEM] Сервер активен. Открой в браузере: http://localhost:8080");
    }

    private static void loadMapNodes() throws SQLException {
        Statement st = conn.createStatement();
        ResultSet rs = st.executeQuery("SELECT id, lat, lng FROM map_nodes");
        while (rs.next()) {
            targetsMap.put(rs.getInt("id"), new TargetNode(rs.getInt("id"), rs.getDouble("lat"), rs.getDouble("lng")));
        }
        System.out.println("[DB] В оперативную память загружены координаты " + targetsMap.size() + " целей.");
    }

    interface Intel { 
        boolean loadDataFromDB(); 
        String getSecretData();   
    }

    static class RealIntel implements Intel {
        private String fullName, photoUrl, bankAccount;
        private double balance;

        public RealIntel(int id) {
            System.out.println("  [БД-ФАЙЛ] Чтение из файла базы данных для ID: " + id);
            try {
                PreparedStatement ps = conn.prepareStatement("SELECT * FROM secret_data WHERE id = ?");
                ps.setInt(1, id);
                ResultSet rs = ps.executeQuery();
                if (rs.next()) {
                    this.fullName = rs.getString("full_name");
                    this.photoUrl = rs.getString("photo_url");
                    this.bankAccount = rs.getString("bank_account");
                    this.balance = rs.getDouble("balance");
                }
            } catch (SQLException e) { e.printStackTrace(); }
        }

        @Override public boolean loadDataFromDB() { return true; }
        
        @Override public String getSecretData() {
            return String.format(Locale.US, "{\"name\":\"%s\", \"photo\":\"%s\", \"bank\":\"%s\", \"balance\":%.2f}",
                    fullName, photoUrl, bankAccount, balance);
        }
    }

    static class ProxyIntel implements Intel {
        private final int id;
        private RealIntel realIntel;

        public void reset() { this.realIntel = null; } 

        public ProxyIntel(int id) { this.id = id; }

        @Override
        public boolean loadDataFromDB() {
            if (realIntel == null) {
                realIntel = new RealIntel(id); 
                return true;
            }
            return false;
        }

        @Override
        public String getSecretData() {
            if (realIntel == null) return "{\"error\":\"REQUIRES_LOAD\"}"; 
            return realIntel.getSecretData();
        }
    }

    static class TargetNode {
        int id; double lat, lng;
        Intel intel;
        public TargetNode(int id, double lat, double lng) {
            this.id = id; this.lat = lat; this.lng = lng;
            this.intel = new ProxyIntel(id);
        }
    }

    static class FrontendHandler implements HttpHandler {
        @Override public void handle(HttpExchange exchange) throws IOException {
            File file = new File("index.html");
            if (!file.exists()) {
                sendHtml(exchange, "<h1 style='color:red;'>Файл index.html не найден в корне проекта!</h1>");
                return;
            }
            String html = new String(Files.readAllBytes(file.toPath()), "UTF-8");
            sendHtml(exchange, html);
        }
    }

    static class MapDataHandler implements HttpHandler {
        @Override public void handle(HttpExchange exchange) throws IOException {
            StringBuilder json = new StringBuilder("[");
            
            for (TargetNode node : targetsMap.values()) {
                json.append(String.format(Locale.US, "{\"id\":%d, \"lat\":%f, \"lng\":%f},", node.id, node.lat, node.lng));
            }

            if (json.length() > 1) {
                json.setLength(json.length() - 1); 
            }
            json.append("]");
            sendJson(exchange, json.toString());
        }
    }

    static class LoadDataHandler implements HttpHandler {
        @Override public void handle(HttpExchange exchange) throws IOException {
            int id = Integer.parseInt(exchange.getRequestURI().getQuery().split("=")[1]);
            TargetNode node = targetsMap.get(id);
            boolean loaded = node.intel.loadDataFromDB();
            sendJson(exchange, "{\"status\":\"" + (loaded ? "ИЗВЛЕЧЕНО ИЗ ФАЙЛА БД" : "УЖЕ В ПАМЯТИ") + "\"}");
        }
    }

    static class HackDataHandler implements HttpHandler {
        @Override public void handle(HttpExchange exchange) throws IOException {
            int id = Integer.parseInt(exchange.getRequestURI().getQuery().split("=")[1]);
            TargetNode node = targetsMap.get(id);
            sendJson(exchange, node.intel.getSecretData());
        }
    }

    private static void sendHtml(HttpExchange exchange, String response) throws IOException {
        exchange.getResponseHeaders().add("Content-Type", "text/html; charset=UTF-8");
        byte[] bytes = response.getBytes("UTF-8");
        exchange.sendResponseHeaders(200, bytes.length);
        OutputStream os = exchange.getResponseBody();
        os.write(bytes);
        os.close();
    }

    private static void sendJson(HttpExchange exchange, String response) throws IOException {
        exchange.getResponseHeaders().add("Content-Type", "application/json; charset=UTF-8");
        byte[] bytes = response.getBytes("UTF-8");
        exchange.sendResponseHeaders(200, bytes.length);
        OutputStream os = exchange.getResponseBody();
        os.write(bytes);
        os.close();
    }

        

    static class PhotoFileHandler implements HttpHandler {
        @Override
        public void handle(HttpExchange exchange) throws IOException {
            String path = exchange.getRequestURI().getPath().substring(1);
            File file = new File(path);

            if (file.exists() && !file.isDirectory()) {
                exchange.getResponseHeaders().add("Content-Type", "image/jpeg");
                byte[] bytes = Files.readAllBytes(file.toPath());
                exchange.sendResponseHeaders(200, bytes.length);
                try (OutputStream os = exchange.getResponseBody()) {
                    os.write(bytes);
                }
            } else {
                System.err.println("Файл не найден: " + path);
                String msg = "404 Not Found";
                exchange.sendResponseHeaders(404, msg.length());
                exchange.getResponseBody().write(msg.getBytes());
                exchange.getResponseBody().close();
            }
        }
    }
    static class StealMoneyHandler implements HttpHandler {
    @Override
    public void handle(HttpExchange exchange) throws IOException {
        int id = Integer.parseInt(exchange.getRequestURI().getQuery().split("=")[1]);
        System.out.println("[BANK_HACK] Попытка хищения средств у ID: " + id);

        try {
            PreparedStatement ps = conn.prepareStatement("UPDATE secret_data SET balance = 0 WHERE id = ?");
            ps.setInt(1, id);
            int rowsUpdated = ps.executeUpdate();

            if (rowsUpdated > 0) {
                TargetNode node = targetsMap.get(id);
                if (node.intel instanceof ProxyIntel) {
                    ((ProxyIntel) node.intel).reset(); 
                }

                sendJson(exchange, "{\"status\":\"SUCCESS\", \"msg\":\"Счет обнулен. Средства переведены на офшор.\"}");
            } else {
                sendJson(exchange, "{\"status\":\"ERROR\", \"msg\":\"Цель не найдена в банковской системе.\"}");
            }
        } catch (SQLException e) {
            e.printStackTrace();
            sendJson(exchange, "{\"status\":\"ERROR\", \"msg\":\"Ошибка банковского шлюза.\"}");
        }
    }
}
}