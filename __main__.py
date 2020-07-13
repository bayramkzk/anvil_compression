from algorithms.anvil import Anvil

import tkinter as tk
from tkinter import ttk

from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter.messagebox import showwarning, showinfo, showerror

from threading import Thread


class AnvilApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # window settings
        self.title('Anvil Kayıpsız Sıkıştırma')
        self.resizable(False, False)
        
        # read "user guide" and "about" files
        self.read_help_files()
        
        # set top bar menu
        self.set_menu()
        
        # set encode - decode notebook
        self.set_notebook()
    
    def read_help_files(self):
        try:
            with open('help/about.txt', 'r', encoding='utf-8') as f:
                self.about_text = f.read()
            
        except FileNotFoundError as e:
            showerror(
                '"help/about.txt" yolunda "Hakkında" dosyası bulunamadı.\n'
                'Lütfen dosyayı sağlayıp tekrar deneyiniz.'
            )
            raise e
            
        try:
            with open('help/user_guide.txt', 'r', encoding='utf-8') as f:
                self.user_guide_text = f.read()
        except FileNotFoundError as e:
            showerror(
                '"help/user_guide.txt" yolunda "Kullanıcı Kılavuzu" dosyası '
                'bulunamadı.\nLütfen dosyayı sağlayıp tekrar deneyiniz.'
            )
            raise e
    
    def set_notebook(self):
        self.notebook = ttk.Notebook(self, width=500)
        
        self.encode_frame = FileFrame(
            file_command=Anvil.encode, 
            start_button_text="ENCODING'E BAŞLA",
            file_types=[
                ('Yazı Dosyaları', '.txt'),
                ('Döküman Belgeleri', '.doc .docx'),
            ],
            file_default_type='.txt',
            save_types=[('Anvil Dosyaları', '*.anvil')],
            save_default_type='.anvil',
        )
        
        self.decode_frame = FileFrame(
            file_command=Anvil.decode, 
            start_button_text="DECODING'E BAŞLA",
            file_types=[('ANVIL Dosyaları', '.anvil')],
            file_default_type='.anvil',
            save_types=[
                ('Yazı Dosyaları', '.txt'),
                ('Döküman Belgeleri', '.doc .docx'),
            ],
            save_default_type='.txt',
        )
        
        self.notebook.add(self.encode_frame)
        self.notebook.add(self.decode_frame)
        
        self.notebook.tab(0, text='Encode', padding=10)
        self.notebook.tab(1, text='Decode', padding=10)
        
        self.notebook.pack(fill='both')
    
    def set_menu(self):
        self.menu = tk.Menu(self)
        
        self.help_menu = tk.Menu(self.menu, tearoff=False)
        self.help_menu.add_command(
            label='Hakkında', 
            command=self.about,
        )
        self.help_menu.add_command(
            label='Kullanım Kılavuzu',
            command=self.user_guide,
        )
        
        self.menu.add_cascade(label='Yardım', menu=self.help_menu)
        self.config(menu=self.menu)
    
    def about(self):
        about_window = tk.Toplevel(self)
        
        about_window.resizable(False, False)
        about_window.title('Hakkında')
        
        about_label = ttk.Label(
            about_window, 
            text=self.about_text,
            justify='center', 
            padding=15,
        )
        
        about_label.pack(fill='both', expand=True)
    
    def user_guide(self):
        user_guide_window = tk.Toplevel(self)
        
        user_guide_window.resizable(False, False)
        user_guide_window.title('Kullanım Kılavuzu')
        
        about_label = ttk.Label(
            user_guide_window,
            text=self.user_guide_text, 
            justify='center',
            padding=15,
        )
        
        about_label.pack(fill='both', expand=True)


class FileFrame(ttk.Frame):
    def __init__(self, *args, file_command, file_default_type, file_types,
                 save_default_type, save_types, start_button_text, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.file_default_type = file_default_type
        self.file_types = file_types
        self.save_default_type = save_default_type
        self.save_types = save_types
        
        self.file_command = file_command
        
        self.file_path: str = None
        self.save_path: str = None
        
        self.file_button_text = 'DOSYA YOLU SEÇ'
        self.save_button_text = 'KAYIT YOLU SEÇ'
        
        self.file_button = ttk.Button(
            self, command=self.select_file_path,
            text=self.file_button_text
        )
        
        self.save_button = ttk.Button(
            self, command=self.select_save_path,
            text=self.save_button_text
        )
        
        self.start_button = ttk.Button(
            self, command=lambda: Thread(target=self.command).start(),
            state='disabled',
            text=start_button_text,
        )
        
        self.progress_bar = ttk.Progressbar(self, orient='horizontal')
        self.progress_bar.config(mode='indeterminate')
        
        self.file_button.pack(fill='x')
        self.save_button.pack(fill='x')
        self.start_button.pack(fill='x')
    
    def select_file_path(self):
        path = askopenfilename(
            filetypes=self.file_types,
            defaultextension=self.file_default_type,
        )
        
        if path:
            self.file_path = path
            self.file_button.config(text=self.file_path)
            
            if self.file_path and self.save_path:
                self.start_button.config(state='normal')
        else:
            self.file_path = None
            self.file_button.config(text=self.file_button_text)
    
    def select_save_path(self):
        path = asksaveasfilename(
            filetypes=self.save_types,
            defaultextension=self.save_default_type,
        )
        
        if path:
            self.save_path = path
            self.save_button.config(text=self.save_path)
            
            if self.file_path and self.save_path:
                self.start_button.config(state='normal')
        else:
            self.save_path = None
            self.save_button.config(text=self.save_button_text)
    
    def command(self):
        self.start_button.pack_forget()
        self.progress_bar.pack(fill='x')
        self.progress_bar.start()
        
        self.file_button.config(state='disabled')
        self.save_button.config(state='disabled')
        
        try:
            self.file_command(self.file_path, self.save_path)
        except Exception as e:
            showerror('Hata', 'Bir hata ile karşılaşıldı:\n' + str(e))
        else:
            showinfo('Başarılı', 'İşleminiz başarıyla gerçekleştirildi!')
        
        self.file_button.config(state='normal', text=self.file_button_text)
        self.save_button.config(state='normal', text=self.save_button_text)
        
        self.progress_bar.stop()
        self.progress_bar.pack_forget()
        self.start_button.pack(fill='x')


if __name__ == '__main__':
    root = AnvilApp()
    root.mainloop()
