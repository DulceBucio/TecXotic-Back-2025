import tkinter as tk
from tkinter import ttk, font
import time
import json

# Datos de presencia de carpas invasoras por año y región
carp_data = {
    2016: {'1': False, '2': False, '3': False, '4': False, '5': False},
    2017: {'1': True, '2': False, '3': False, '4': False, '5': False},
    2018: {'1': True, '2': False, '3': False, '4': False, '5': False},
    2019: {'1': True, '2': False, '3': False, '4': False, '5': False},
    2020: {'1': True, '2': True, '3': True, '4': False, '5': False},
    2021: {'1': True, '2': True, '3': True, '4': False, '5': False},
    2022: {'1': True, '2': True, '3': True, '4': False, '5': False},
    2023: {'1': True, '2': True, '3': True, '4': True, '5': False},
    2024: {'1': True, '2': True, '3': True, '4': True, '5': False},
    2025: {'1': True, '2': True, '3': True, '4': True, '5': False}
}

class CarpPropagationModel:
    def __init__(self, root):
        self.root = root
        self.root.title("Modelo de Propagación de Carpas Invasoras")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # Variables
        self.years = list(carp_data.keys())
        self.current_year_idx = 0
        self.current_year = self.years[self.current_year_idx]
        self.is_playing = False
        self.play_speed = 1000  # milisegundos
        
        # Configurar fuentes
        self.title_font = font.Font(family="Arial", size=16, weight="bold")
        self.subtitle_font = font.Font(family="Arial", size=12, weight="bold")
        self.normal_font = font.Font(family="Arial", size=10)
        
        # Crear el marco principal
        self.main_frame = ttk.Frame(root, padding=10)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        self.title_label = ttk.Label(
            self.main_frame, 
            text="Propagación de Carpas Invasoras en la Cuenca del Río Illinois",
            font=self.title_font
        )
        self.title_label.pack(pady=10)
        
        # Marco para el año actual
        self.year_frame = ttk.Frame(self.main_frame)
        self.year_frame.pack(pady=5)
        
        self.year_label = ttk.Label(
            self.year_frame,
            text=f"Año: {self.current_year}",
            font=self.subtitle_font
        )
        self.year_label.pack(side=tk.LEFT, padx=10)
        
        # Controles de reproducción
        self.controls_frame = ttk.Frame(self.main_frame)
        self.controls_frame.pack(pady=5)
        
        self.prev_button = ttk.Button(
            self.controls_frame,
            text="◀ Anterior",
            command=self.previous_year
        )
        self.prev_button.pack(side=tk.LEFT, padx=5)
        
        self.play_button = ttk.Button(
            self.controls_frame,
            text="▶ Reproducir",
            command=self.toggle_play
        )
        self.play_button.pack(side=tk.LEFT, padx=5)
        
        self.next_button = ttk.Button(
            self.controls_frame,
            text="Siguiente ▶",
            command=self.next_year
        )
        self.next_button.pack(side=tk.LEFT, padx=5)
        
        self.reset_button = ttk.Button(
            self.controls_frame,
            text="⟳ Reiniciar",
            command=self.reset_animation
        )
        self.reset_button.pack(side=tk.LEFT, padx=5)
        
        # Barra deslizante para el año
        self.slider_frame = ttk.Frame(self.main_frame)
        self.slider_frame.pack(fill=tk.X, pady=10, padx=20)
        
        self.year_slider = ttk.Scale(
            self.slider_frame,
            from_=0,
            to=len(self.years) - 1,
            orient=tk.HORIZONTAL,
            command=self.slider_changed
        )
        self.year_slider.pack(fill=tk.X)
        
        # Etiquetas de años para la barra deslizante
        self.slider_labels_frame = ttk.Frame(self.slider_frame)
        self.slider_labels_frame.pack(fill=tk.X)
        
        for i, year in enumerate(self.years):
            position = i / (len(self.years) - 1)
            label = ttk.Label(self.slider_labels_frame, text=str(year))
            label.place(relx=position, anchor=tk.N)
        
        # Marco para el mapa
        self.map_frame = ttk.Frame(self.main_frame)
        self.map_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Canvas para dibujar el mapa
        self.canvas = tk.Canvas(self.map_frame, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Coordenadas de las regiones (simplificadas)
        self.region_coords = {
            '1': [(50, 100), (150, 100), (150, 200), (50, 200)],
            '2': [(150, 100), (250, 100), (250, 200), (150, 200)],
            '3': [(250, 100), (350, 100), (350, 200), (250, 200)],
            '4': [(350, 100), (450, 100), (450, 200), (350, 200)],
            '5': [(450, 100), (550, 100), (550, 200), (450, 200)]
        }
        
        # Dibujar el río
        self.canvas.create_line(50, 250, 550, 250, width=5, fill="blue")
        self.canvas.create_text(300, 270, text="Río Illinois", font=self.subtitle_font, fill="blue")
        
        # Marco para la tabla de datos
        self.data_frame = ttk.Frame(self.main_frame)
        self.data_frame.pack(fill=tk.X, pady=10)
        
        # Leyenda
        self.legend_frame = ttk.Frame(self.data_frame)
        self.legend_frame.pack(pady=5)
        
        self.canvas_red = tk.Canvas(self.legend_frame, width=20, height=20, bg="red")
        self.canvas_red.pack(side=tk.LEFT, padx=5)
        
        self.label_red = ttk.Label(self.legend_frame, text="Carpas invasoras presentes")
        self.label_red.pack(side=tk.LEFT, padx=5)
        
        self.canvas_green = tk.Canvas(self.legend_frame, width=20, height=20, bg="green")
        self.canvas_green.pack(side=tk.LEFT, padx=20)
        
        self.label_green = ttk.Label(self.legend_frame, text="Sin carpas invasoras")
        self.label_green.pack(side=tk.LEFT, padx=5)
        
        # Tabla de datos históricos
        self.table_frame = ttk.Frame(self.main_frame)
        self.table_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.table_label = ttk.Label(
            self.table_frame,
            text="Datos históricos de presencia de carpas invasoras",
            font=self.subtitle_font
        )
        self.table_label.pack(pady=5)
        
        # Crear tabla
        self.table = ttk.Treeview(self.table_frame, columns=tuple(range(1, 6)), show="headings")
        
        # Configurar encabezados
        self.table.heading(0, text="Año")
        for i in range(1, 6):
            self.table.heading(i, text=f"Región {i}")
        
        # Configurar columnas
        self.table.column(0, width=80, anchor=tk.CENTER)
        for i in range(1, 6):
            self.table.column(i, width=80, anchor=tk.CENTER)
        
        # Scrollbar para la tabla
        self.scrollbar = ttk.Scrollbar(self.table_frame, orient=tk.VERTICAL, command=self.table.yview)
        self.table.configure(yscrollcommand=self.scrollbar.set)
        
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.table.pack(fill=tk.BOTH, expand=True)
        
        # Inicializar la visualización
        self.update_display()
        
        # Vincular evento de redimensionamiento
        self.root.bind("<Configure>", self.on_resize)
    
    def on_resize(self, event):
        """Manejar el redimensionamiento de la ventana."""
        # Solo redimensionar si el evento proviene de la ventana principal
        if event.widget == self.root:
            self.update_display()
    
    def update_display(self):
        """Actualizar toda la visualización para el año actual."""
        self.year_label.config(text=f"Año: {self.current_year}")
        self.year_slider.set(self.current_year_idx)
        self.draw_map()
        self.update_table()
    
    def draw_map(self):
        """Dibujar el mapa con las regiones coloreadas según la presencia de carpas."""
        # Limpiar el canvas
        self.canvas.delete("region")
        
        # Obtener dimensiones del canvas
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        # Ajustar coordenadas si el canvas tiene un tamaño razonable
        if canvas_width > 100 and canvas_height > 100:
            scale_x = canvas_width / 600
            scale_y = canvas_height / 400
            
            # Dibujar las regiones
            for region, coords in self.region_coords.items():
                # Escalar coordenadas
                scaled_coords = []
                for x, y in coords:
                    scaled_coords.append(x * scale_x)
                    scaled_coords.append(y * scale_y)
                
                # Determinar color según presencia de carpas
                has_carp = carp_data[self.current_year][region]
                color = "red" if has_carp else "green"
                
                # Dibujar polígono
                self.canvas.create_polygon(
                    scaled_coords,
                    fill=color,
                    outline="white",
                    width=2,
                    tags="region"
                )
                
                # Calcular centro para la etiqueta
                center_x = sum(scaled_coords[::2]) / 4
                center_y = sum(scaled_coords[1::2]) / 4
                
                # Añadir etiqueta de región
                self.canvas.create_text(
                    center_x,
                    center_y,
                    text=f"Región {region}",
                    fill="white",
                    font=self.normal_font,
                    tags="region"
                )
            
            # Redibujar el río
            self.canvas.delete("river")
            river_y = canvas_height * 0.6
            self.canvas.create_line(
                50 * scale_x, river_y,
                550 * scale_x, river_y,
                width=5,
                fill="blue",
                tags="river"
            )
            self.canvas.create_text(
                canvas_width / 2,
                river_y + 20,
                text="Río Illinois",
                font=self.subtitle_font,
                fill="blue",
                tags="river"
            )
    
    def update_table(self):
        """Actualizar la tabla de datos históricos."""
        # Limpiar tabla
        for item in self.table.get_children():
            self.table.delete(item)
        
        # Añadir filas para cada año hasta el actual
        for year in self.years:
            if year <= self.current_year:
                values = [year]
                for region in range(1, 6):
                    values.append("Sí" if carp_data[year][str(region)] else "No")
                
                self.table.insert("", tk.END, values=values)
    
    def slider_changed(self, value):
        """Manejar cambios en la barra deslizante."""
        idx = int(float(value))
        if idx != self.current_year_idx:
            self.current_year_idx = idx
            self.current_year = self.years[idx]
            self.update_display()
    
    def next_year(self):
        """Avanzar al siguiente año."""
        if self.current_year_idx < len(self.years) - 1:
            self.current_year_idx += 1
            self.current_year = self.years[self.current_year_idx]
            self.update_display()
    
    def previous_year(self):
        """Retroceder al año anterior."""
        if self.current_year_idx > 0:
            self.current_year_idx -= 1
            self.current_year = self.years[self.current_year_idx]
            self.update_display()
    
    def toggle_play(self):
        """Alternar entre reproducir y pausar la animación."""
        self.is_playing = not self.is_playing
        
        if self.is_playing:
            self.play_button.config(text="⏸ Pausar")
            self.play_animation()
        else:
            self.play_button.config(text="▶ Reproducir")
    
    def play_animation(self):
        """Reproducir la animación automáticamente."""
        if self.is_playing:
            if self.current_year_idx < len(self.years) - 1:
                self.next_year()
                self.root.after(self.play_speed, self.play_animation)
            else:
                self.is_playing = False
                self.play_button.config(text="▶ Reproducir")
    
    def reset_animation(self):
        """Reiniciar la animación al primer año."""
        self.is_playing = False
        self.play_button.config(text="▶ Reproducir")
        self.current_year_idx = 0
        self.current_year = self.years[0]
        self.update_display()

    def export_to_json(self):
        """Exportar los datos a un archivo JSON."""
        with open("carp_propagation_data.json", "w") as f:
            json.dump(carp_data, f, indent=4)
        print("Datos exportados a carp_propagation_data.json")

def main():
    root = tk.Tk()
    app = CarpPropagationModel(root)
    root.mainloop()

if __name__ == "__main__":
    main()