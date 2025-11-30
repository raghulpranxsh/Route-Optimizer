import tkinter as tk
from tkinter import messagebox
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import heapq

# Function to get coordinates from a pincode
def get_coordinates_from_pincode(pincode):
    geolocator = Nominatim(user_agent="delivery_app")
    location = geolocator.geocode(pincode)
    if location:
        return (location.latitude, location.longitude)
    else:
        return None

# Function to calculate distance between two pin codes
def calculate_distance(pincode1, pincode2):
    coords_1 = get_coordinates_from_pincode(pincode1)
    coords_2 = get_coordinates_from_pincode(pincode2)
    
    if coords_1 and coords_2:
        return geodesic(coords_1, coords_2).kilometers
    else:
        return float('inf')

# Dijkstra's algorithm implementation
def dijkstra(graph, start, end):
    queue = [(0, start)]  
    distances = {node: float('inf') for node in graph}
    distances[start] = 0
    previous_nodes = {node: None for node in graph}
    visited = set()  
    
    while queue:
        current_distance, current_node = heapq.heappop(queue)
        
        if current_node in visited:
            continue
        
        visited.add(current_node)

        if current_node == end:
            break  
        
        for neighbor, distance in graph[current_node].items():
            total_distance = current_distance + distance
            
            if total_distance < distances[neighbor]:
                distances[neighbor] = total_distance
                previous_nodes[neighbor] = current_node
                heapq.heappush(queue, (total_distance, neighbor))
    
    # Backtrack to find the path
    path, node = [], end
    while previous_nodes[node] is not None:
        path.insert(0, node)
        node = previous_nodes[node]
    if path:
        path.insert(0, node)
    
    return path, distances[end]

# Find the nearest delivery station to a pin code
def find_nearest_station(pincode, stations):
    min_distance = float('inf')
    nearest_station = None
    for station, station_pincode in stations.items():
        distance = calculate_distance(pincode, station_pincode)
        if distance < min_distance:
            min_distance = distance
            nearest_station = station
    return nearest_station, min_distance

# GUI Setup
class DeliveryApp(tk.Tk):
    def __init__(self, graph, stations):
        super().__init__()
        self.title("Delivery Route Planner - Coimbatore")
        self.geometry("800x600")
        self.configure(bg="#f0f0f0")
        self.graph = graph
        self.stations = stations
        
        self.label_start = tk.Label(self, text="Seller's Pin Code:", font=("Helvetica", 12), bg="#f0f0f0")
        self.label_start.pack(pady=10)
        
        self.entry_start = tk.Entry(self, font=("Helvetica", 12), width=25)
        self.entry_start.pack(pady=5)
        
        self.label_destination = tk.Label(self, text="Delivery Pin Code:", font=("Helvetica", 12), bg="#f0f0f0")
        self.label_destination.pack(pady=10)
        
        self.entry_destination = tk.Entry(self, font=("Helvetica", 12), width=25)
        self.entry_destination.pack(pady=5)
        
        self.button = tk.Button(self, text="Find Optimal Route", font=("Helvetica", 12), bg="#4CAF50", fg="white", command=self.find_route)
        self.button.pack(pady=20)
        
        self.canvas = tk.Canvas(self, width=700, height=400, bg="white", relief="sunken", borderwidth=2)
        self.canvas.pack(pady=20)
        self.node_positions = {}  

    def draw_graph(self, path=[]):
        
        self.canvas.delete("all")
        
        # Define positions for each station on the canvas
        positions = {
            'Coimbatore Central': (100, 300),
            'Gandhipuram': (300, 100),
            'RS Puram': (500, 300),
            'Peelamedu': (200, 400),
            'Ukkadam': (400, 400),
            'Tidel Park': (200, 250),
            'Avinashi Road': (300, 250),
            'Kuniamuthur': (100, 150),
            'Mettupalayam': (600, 100),
            'Saravanampatti': (500, 200)
        }
        
        self.node_positions = positions
        
        # Draw all nodes
        for station, pos in positions.items():
            x, y = pos
            self.canvas.create_oval(x-10, y-10, x+10, y+10, fill='blue')
            self.canvas.create_text(x, y, text=station, fill='black', font=("Helvetica", 10))
        
        for station, neighbors in self.graph.items():
            for neighbor, distance in neighbors.items():
                x1, y1 = positions[station]
                x2, y2 = positions[neighbor]
                
                if station in path and neighbor in path:
                    self.canvas.create_line(x1, y1, x2, y2, fill='green', width=2)
                    mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
                    self.canvas.create_text(mid_x, mid_y, text=f"{distance:.2f} km", fill='red', font=("Helvetica", 8))

                elif station in self.graph and neighbor in self.graph[station]:
                    self.canvas.create_line(x1, y1, x2, y2, fill='lightgray')

    def find_route(self):
        start_pin = self.entry_start.get().strip()
        dest_pin = self.entry_destination.get().strip()
        
        nearest_start, start_to_station = find_nearest_station(start_pin, self.stations)
        nearest_end, station_to_end = find_nearest_station(dest_pin, self.stations)
        
        if nearest_start is None or nearest_end is None:
            messagebox.showerror("Error", "Could not find nearest delivery stations. Please check the inputs.")
            return
        
        path, total_distance = dijkstra(self.graph, nearest_start, nearest_end)
        
        if not path:
            messagebox.showerror("Error", "No available route found.")
            return
        
        detailed_message = "Optimal route found:\n"
        detailed_message += f"Distance from Seller's location ({start_pin}) to {nearest_start}: {start_to_station:.2f} km\n"
        for i in range(len(path)-1):
            distance_between = self.graph[path[i]][path[i+1]]
            detailed_message += f"Distance from {path[i]} to {path[i+1]}: {distance_between:.2f} km\n"
        detailed_message += f"Distance from {nearest_end} to Customer location ({dest_pin}): {station_to_end:.2f} km\n"
        detailed_message += f"Total distance: {total_distance + start_to_station + station_to_end:.2f} km"
        
        result_window = tk.Toplevel(self)
        result_window.title("Route Result")
        result_window.geometry("400x300")
        result_window.configure(bg="#f0f0f0")
        
        result_label = tk.Label(result_window, text=detailed_message, font=("Helvetica", 12), bg="#f0f0f0")
        result_label.pack(pady=20)
        
        self.draw_graph(path)  

# Coimbatore delivery stations with real pin codes
stations = {
    'Coimbatore Central': '641001',  
    'Gandhipuram': '641012',         
    'RS Puram': '641002',            
    'Peelamedu': '641004',           
    'Ukkadam': '641008',             
    'Tidel Park': '641014',           
    'Avinashi Road': '641016',        
    'Kuniamuthur': '641008',          
    'Mettupalayam': '641301',         
    'Saravanampatti': '641035'        
}


graph = {
    'Coimbatore Central': {
        'Gandhipuram': calculate_distance('641001', '641012'), 
        'RS Puram': calculate_distance('641001', '641002'),
        'Tidel Park': calculate_distance('641001', '641014')
    },
    'Gandhipuram': {
        'Coimbatore Central': calculate_distance('641012', '641001'), 
        'Peelamedu': calculate_distance('641012', '641004'),
        'Ukkadam': calculate_distance('641012', '641008')
    },
    'RS Puram': {
        'Coimbatore Central': calculate_distance('641002', '641001'), 
        'Peelamedu': calculate_distance('641002', '641004'),
        'Tidel Park': calculate_distance('641002', '641014')
    },
    'Peelamedu': {
        'Gandhipuram': calculate_distance('641004', '641012'), 
        'RS Puram': calculate_distance('641004', '641002'),
        'Ukkadam': calculate_distance('641004', '641008'),
        'Tidel Park': calculate_distance('641004', '641014')
    },
    'Ukkadam': {
        'Gandhipuram': calculate_distance('641008', '641012'), 
        'Peelamedu': calculate_distance('641008', '641004'),
        'Saravanampatti': calculate_distance('641008', '641035')
    },
    'Tidel Park': {
        'Coimbatore Central': calculate_distance('641014', '641001'), 
        'RS Puram': calculate_distance('641014', '641002'),
        'Peelamedu': calculate_distance('641014', '641004')
    },
    'Avinashi Road': {
        'Gandhipuram': calculate_distance('641016', '641012'), 
        'Saravanampatti': calculate_distance('641016', '641035')
    },
    'Kuniamuthur': {
        'Ukkadam': calculate_distance('641008', '641008')
    },
    'Mettupalayam': {
        'Saravanampatti': calculate_distance('641301', '641035')
    },
    'Saravanampatti': {
        'Ukkadam': calculate_distance('641035', '641008'), 
        'Avinashi Road': calculate_distance('641035', '641016')
    }
}

# Run the application
if __name__ == "__main__":
    app = DeliveryApp(graph, stations)
    app.mainloop()
