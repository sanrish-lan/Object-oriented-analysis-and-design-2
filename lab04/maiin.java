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

public class maiin {
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
        loadAllDataIntoMemory();
        long endTime = System.currentTimeMillis();
        System.out.println(">>> ВРЕМЯ ЗАГРУЗКИ ДАННЫХ: " + (endTime - startTime) + " мс");


        HttpServer server = HttpServer.create(new InetSocketAddress(8090), 0);
        server.createContext("/", new FrontendHandler());
        server.createContext("/api/targets", new MapDataHandler());
        server.createContext("/api/load", new LoadDataHandler());
        server.createContext("/api/hack", new HackDataHandler());
        server.createContext("/photos/", new PhotoFileHandler());
        server.createContext("/api/steal", new StealMoneyHandler());
        server.start();
        
        System.out.println("[SYSTEM] Сервер активен. Открой в браузере: http://localhost:8090");
    }

    private static void loadAllDataIntoMemory() throws SQLException {
        System.out.println("[DB] Начинается полная (жадная) загрузка базы данных в RAM...");
        Statement st = conn.createStatement();
        
        String sql = "SELECT m.id, m.lat, m.lng, s.full_name, s.photo_url, s.bank_account, s.balance " +
                     "FROM map_nodes m " +
                     "JOIN secret_data s ON m.id = s.id";
                     
        ResultSet rs = st.executeQuery(sql);
        while (rs.next()) {
            targetsMap.put(rs.getInt("id"), new TargetNode(
                rs.getInt("id"), 
                rs.getDouble("lat"), 
                rs.getDouble("lng"),
                rs.getString("full_name"),
                rs.getString("photo_url"),
                rs.getString("bank_account"),
                rs.getDouble("balance")
            ));
        }
        System.out.println("[DB] В оперативную память загружены ПОЛНЫЕ ДОСЬЕ для " + targetsMap.size() + " целей.");
        System.out.println("[WARNING] Память сервера сильно загружена!");
    }

    static class TargetNode {
        int id; 
        double lat, lng;
        
        String fullName, photoUrl, bankAccount;
        double balance;

        public TargetNode(int id, double lat, double lng, String fullName, String photoUrl, String bankAccount, double balance) {
            this.id = id; 
            this.lat = lat; 
            this.lng = lng;
            this.fullName = fullName;
            this.photoUrl = photoUrl;
            this.bankAccount = bankAccount;
            this.balance = balance;
        }

        public String getSecretData() {
            return String.format(Locale.US, "{\"name\":\"%s\", \"photo\":\"%s\", \"bank\":\"%s\", \"balance\":%.2f}",
                    fullName, photoUrl, bankAccount, balance);
        }
    }

    static class FrontendHandler implements HttpHandler {
        @Override public void handle(HttpExchange exchange) throws IOException {
            File file = new File("index.html");
            if (!file.exists()) {
                sendHtml(exchange, "<h1 style='color:red;'>Файл index.html не найден!</h1>");
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
            sendJson(exchange, "{\"status\":\"УЖЕ В ПАМЯТИ (ЖАДНАЯ ЗАГРУЗКА)\"}");
        }
    }

    static class HackDataHandler implements HttpHandler {
        @Override public void handle(HttpExchange exchange) throws IOException {
            int id = Integer.parseInt(exchange.getRequestURI().getQuery().split("=")[1]);
            TargetNode node = targetsMap.get(id);
            sendJson(exchange, node.getSecretData());
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
                    node.balance = 0.0;

                    sendJson(exchange, "{\"status\":\"SUCCESS\", \"msg\":\"Счет обнулен. Средства переведены на офшор.\"}");
                } else {
                    sendJson(exchange, "{\"status\":\"ERROR\", \"msg\":\"Цель не найдена.\"}");
                }
            } catch (SQLException e) {
                e.printStackTrace();
                sendJson(exchange, "{\"status\":\"ERROR\", \"msg\":\"Ошибка банковского шлюза.\"}");
            }
        }
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
                String msg = "404 Not Found";
                exchange.sendResponseHeaders(404, msg.length());
                exchange.getResponseBody().write(msg.getBytes());
                exchange.getResponseBody().close();
            }
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
}