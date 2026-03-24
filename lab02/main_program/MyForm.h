#pragma once
#include <msclr/marshal_cppstd.h>
#include "TikTokFacade.h"
#include "Subsystems.h"

namespace TikTokManager {

    using namespace System;
    using namespace System::Windows::Forms;
    using namespace System::Drawing;
    using namespace System::Threading;

    ref class WorkerArgs {
    public:
        String^ Path;
        int Duration;
        String^ Caption;
        bool IsFacade;
    };

    public ref class MyForm : public Form {
    private:
        TextBox^ txtPath;
        Button^ btnBrowse;
        ComboBox^ cmbDuration;
        TextBox^ txtCaption;
        Button^ btnNoPattern;
        Button^ btnPattern;

        delegate void WorkCompletedDelegate(bool success, String^ message);

        std::string toUTF8(String^ managedString) {
            if (managedString == nullptr) return "";
            array<unsigned char>^ bytes = System::Text::Encoding::UTF8->GetBytes(managedString);
            pin_ptr<unsigned char> pinnedBytes = &bytes[0];
            return std::string(reinterpret_cast<char*>(pinnedBytes), bytes->Length);
        }

    public:
        MyForm(void) {
            InitializeComponent();
        }

    private:
        void InitializeComponent(void) {
            this->Text = "Shorts Splitter & Uploader (Final Lab)";
            this->Size = System::Drawing::Size(460, 380);
            this->StartPosition = FormStartPosition::CenterScreen;
            this->BackColor = Color::WhiteSmoke;

            Label^ lblPath = gcnew Label(); lblPath->Text = "Путь к видео (.mp4):"; lblPath->Location = Point(20, 20); lblPath->Width = 250;
            txtPath = gcnew TextBox(); txtPath->Location = Point(20, 40); txtPath->Width = 330;
            btnBrowse = gcnew Button(); btnBrowse->Text = "..."; btnBrowse->Location = Point(360, 39); btnBrowse->Width = 50;
            btnBrowse->Click += gcnew EventHandler(this, &MyForm::OnBrowseClicked);

            Label^ lblDur = gcnew Label(); lblDur->Text = "Разрезать на куски по (сек):"; lblDur->Location = Point(20, 80); lblDur->Width = 250;
            cmbDuration = gcnew ComboBox(); cmbDuration->Location = Point(20, 100); cmbDuration->Width = 100;
            cmbDuration->DropDownStyle = ComboBoxStyle::DropDownList;
            cmbDuration->Items->Add("15"); cmbDuration->Items->Add("30"); cmbDuration->SelectedIndex = 0;

            Label^ lblCap = gcnew Label(); lblCap->Text = "Описание (поддерживает UTF-8):"; lblCap->Location = Point(20, 140); lblCap->Width = 250;
            txtCaption = gcnew TextBox(); txtCaption->Location = Point(20, 160); txtCaption->Width = 400;
            txtCaption->Multiline = true; txtCaption->Height = 60; txtCaption->Text = "My new video #lab";

            btnNoPattern = gcnew Button(); btnNoPattern->Text = "НЕ ПАТТЕРН\n(Цикл в форме)"; btnNoPattern->Location = Point(20, 250);
            btnNoPattern->Width = 195; btnNoPattern->Height = 60; btnNoPattern->BackColor = Color::LightCoral;
            btnNoPattern->Click += gcnew EventHandler(this, &MyForm::OnNoPatternClicked);

            btnPattern = gcnew Button(); btnPattern->Text = "ФАСАД\n(Чистый вызов)"; btnPattern->Location = Point(225, 250);
            btnPattern->Width = 195; btnPattern->Height = 60; btnPattern->BackColor = Color::LightGreen;
            btnPattern->Click += gcnew EventHandler(this, &MyForm::OnPatternClicked);

            this->Controls->Add(lblPath); this->Controls->Add(txtPath); this->Controls->Add(btnBrowse);
            this->Controls->Add(lblDur); this->Controls->Add(cmbDuration);
            this->Controls->Add(lblCap); this->Controls->Add(txtCaption);
            this->Controls->Add(btnNoPattern); this->Controls->Add(btnPattern);
        }

        void OnBrowseClicked(Object^ sender, EventArgs^ e) {
            OpenFileDialog^ ofd = gcnew OpenFileDialog();
            ofd->Filter = "Video Files|*.mp4";
            if (ofd->ShowDialog() == System::Windows::Forms::DialogResult::OK) {
                txtPath->Text = ofd->FileName;
            }
        }

        void SetUIState(bool enabled) {
            btnNoPattern->Enabled = enabled;
            btnPattern->Enabled = enabled;
            btnBrowse->Enabled = enabled;
            if (!enabled) this->Text = "Выполняется обработка и загрузка...";
            else this->Text = "Shorts Splitter & Uploader (Final Lab)";
        }

        void OnNoPatternClicked(Object^ sender, EventArgs^ e) { StartTask(false); }
        void OnPatternClicked(Object^ sender, EventArgs^ e) { StartTask(true); }

        void StartTask(bool useFacade) {
            WorkerArgs^ args = gcnew WorkerArgs();
            args->Path = txtPath->Text;
            args->Caption = txtCaption->Text;
            args->Duration = Convert::ToInt32(cmbDuration->SelectedItem);
            args->IsFacade = useFacade;

            SetUIState(false);
            ThreadPool::QueueUserWorkItem(gcnew WaitCallback(this, &MyForm::DoWork), args);
        }

        void DoWork(Object^ state) {
            WorkerArgs^ args = (WorkerArgs^)state;
            bool ok = false;

            std::string path = toUTF8(args->Path);
            std::string caption = toUTF8(args->Caption);
            int duration = args->Duration;

            if (args->IsFacade) {
                TikTokFacade facade;
                ok = facade.ProcessAndUpload(path, duration, caption);
            }
            else {
                FileValidator v; VideoEditor ed; CoverExtractor ce; NetworkUploader up;
                if (v.CheckFile(path)) {
                    int total = v.GetDuration(path);
                    ok = true;
                    for (int s = 0, p = 1; s < total; s += duration, p++) {
                        std::string vp = "np_part_" + std::to_string(p) + ".mp4";
                        std::string cp = "np_part_" + std::to_string(p) + ".jpg";
                        if (ed.CutAndRotate(path, vp, s, duration)) {
                            ce.CreateCover(vp, cp);
                            if (!up.Upload(vp, caption + " (Part " + std::to_string(p) + ")", "http://100.69.137.26:8000/api/upload")) ok = false;
                            std::remove(vp.c_str()); std::remove(cp.c_str());
                        }
                    }
                }
            }

            this->Invoke(gcnew WorkCompletedDelegate(this, &MyForm::OnWorkCompleted), ok, ok ? "Все части успешно загружены!" : "Произошла ошибка!");
        }

        void OnWorkCompleted(bool success, String^ message) {
            SetUIState(true);
            MessageBox::Show(message, success ? "Успех" : "Ошибка", MessageBoxButtons::OK, success ? MessageBoxIcon::Information : MessageBoxIcon::Error);
        }
    };
}