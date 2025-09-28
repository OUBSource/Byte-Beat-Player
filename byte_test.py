import tkinter as tk
from tkinter import ttk
import pyaudio
import threading
import time

class ByteBeatPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("Byte Beat Player")
        self.root.geometry("600x400")
        
        self.is_playing = False
        self.audio_stream = None
        self.p = pyaudio.PyAudio()
        
        # Переменные для byte beat
        self.t = 0
        self.sample_rate = 8000
        
        self.setup_ui()
        
    def setup_ui(self):
        # Основной фрейм
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Заголовок
        title_label = ttk.Label(main_frame, text="Byte Beat Player", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Поле для ввода формулы
        formula_label = ttk.Label(main_frame, text="Byte Beat Formula:")
        formula_label.grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        
        self.formula_entry = tk.Text(main_frame, height=4, width=60, font=("Consolas", 10))
        self.formula_entry.grid(row=2, column=0, columnspan=2, pady=(0, 10))
        self.formula_entry.insert("1.0", "t*(234&t>>10)")
        
        # Примеры формул
        examples_label = ttk.Label(main_frame, text="Примеры формул:")
        examples_label.grid(row=3, column=0, sticky=tk.W, pady=(10, 5))
        
        examples = [
            "t*(234&t>>10)",
            "(t>>5)|(t<<3)",
            "t*((t>>9|t>>13)&15)&t>>5",
            "(t>>7|t|t>>6)*10+4*(t&t>>13|t>>6)"
        ]
        
        for i, example in enumerate(examples):
            example_btn = ttk.Button(main_frame, text=example, 
                                   command=lambda ex=example: self.set_formula(ex))
            example_btn.grid(row=4+i, column=0, columnspan=2, sticky=tk.W+tk.E, pady=2)
        
        # Кнопки управления
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=8, column=0, columnspan=2, pady=20)
        
        self.play_button = ttk.Button(button_frame, text="Play", command=self.toggle_play)
        self.play_button.grid(row=0, column=0, padx=5)
        
        ttk.Button(button_frame, text="Stop", command=self.stop).grid(row=0, column=1, padx=5)
        
        # Статус
        self.status_label = ttk.Label(main_frame, text="Status: Stopped", foreground="red")
        self.status_label.grid(row=9, column=0, columnspan=2, pady=10)
        
        # Информация
        info_text = """
        Используйте переменную 't' для времени
        Поддерживаемые операции: +, -, *, /, &, |, >>, <<, %
        Формула вычисляется для каждого семпла: sample = formula(t) % 256
        """
        info_label = ttk.Label(main_frame, text=info_text, justify=tk.LEFT)
        info_label.grid(row=10, column=0, columnspan=2, pady=10)
        
        # Настройка расширения
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
    
    def set_formula(self, formula):
        self.formula_entry.delete("1.0", tk.END)
        self.formula_entry.insert("1.0", formula)
    
    def evaluate_formula(self, t):
        try:
            formula = self.formula_entry.get("1.0", tk.END).strip()
            # Безопасное выполнение формулы
            result = eval(formula, {"t": t, "__builtins__": {}})
            return int(result) % 256
        except:
            return 0
    
    def audio_callback(self, in_data, frame_count, time_info, status):
        if not self.is_playing:
            return (b'\x00' * frame_count, pyaudio.paComplete)
        
        data = bytearray()
        for i in range(frame_count):
            sample = self.evaluate_formula(self.t)
            data.append(sample)
            self.t += 1
        
        return (bytes(data), pyaudio.paContinue)
    
    def toggle_play(self):
        if not self.is_playing:
            self.start_playback()
        else:
            self.pause_playback()
    
    def start_playback(self):
        if self.is_playing:
            return
            
        self.is_playing = True
        self.t = 0
        
        if self.audio_stream is None:
            self.audio_stream = self.p.open(
                format=pyaudio.paUInt8,
                channels=1,
                rate=self.sample_rate,
                output=True,
                stream_callback=self.audio_callback,
                frames_per_buffer=1024
            )
            self.audio_stream.start_stream()
        
        self.play_button.config(text="Pause")
        self.status_label.config(text="Status: Playing", foreground="green")
    
    def pause_playback(self):
        self.is_playing = False
        self.play_button.config(text="Play")
        self.status_label.config(text="Status: Paused", foreground="orange")
    
    def stop(self):
        self.is_playing = False
        self.t = 0
        
        if self.audio_stream is not None:
            self.audio_stream.stop_stream()
            self.audio_stream.close()
            self.audio_stream = None
        
        self.play_button.config(text="Play")
        self.status_label.config(text="Status: Stopped", foreground="red")
    
    def on_closing(self):
        self.stop()
        self.p.terminate()
        self.root.destroy()

def main():
    root = tk.Tk()
    app = ByteBeatPlayer(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()