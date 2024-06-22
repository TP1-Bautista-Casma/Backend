import numpy as np
from PIL import Image
import cv2
from scipy.optimize import minimize
from sklearn.cluster import MiniBatchKMeans
from PIL import Image


def get_transformation_matrix(cone_type):
    # Matrices de transformación específicas para cada tipo de cono anómalo
    if cone_type == 'protanomalous':
        T_anom = np.array([[0.817, 0.183, 0.0],
                           [0.333, 0.667, 0.0],
                           [0.0, 0.125, 0.875]])  # Matriz de transformación para protanomalía
    elif cone_type == 'deuteranomalous':
        T_anom = np.array([[0.8, 0.2, 0.0],
                           [0.258, 0.742, 0.0],
                           [0.0, 0.142, 0.858]])  # Matriz de transformación para deuteranomalía
    elif cone_type == 'tritanomalous':
        T_anom = np.array([[0.967, 0.033, 0.0],
                           [0.0, 0.733, 0.267],
                           [0.0, 0.183, 0.817]])  # Matriz de transformación para tritanomalía
    else:
        raise ValueError("Tipo de cono anómalo no reconocido")

    return T_anom

def adapt_colors_for_anomalous_trichromat(image_path, cone_type):
    # Cargar la imagen original
    original_image = Image.open(image_path).convert('RGB')
    width, height = original_image.size

    # Obtener los píxeles de la imagen original
    pixels = original_image.load()

    # Crear una nueva imagen para la adaptada
    adapted_image = Image.new("RGB", (width, height))
    adapted_pixels = adapted_image.load()

    # Obtener la matriz de corrección de color
    color_matrix = get_transformation_matrix(cone_type)

    # Iterar sobre cada píxel de la imagen y adaptar sus colores
    for y in range(height):
        for x in range(width):
            # Obtener los valores de los canales RGB del píxel actual
            R, G, B = pixels[x, y]

            # Convertir los valores de los canales RGB a un vector columna
            RGB_orig = np.array([R, G, B])

            # Aplicar la matriz de corrección de color
            RGB_corrected = np.dot(color_matrix, RGB_orig)

            # Asegurar que los valores estén en el rango [0, 255]
            RGB_corrected = np.clip(RGB_corrected, 0, 255)

            # Convertir el resultado de vuelta a los valores RGB
            R_corrected, G_corrected, B_corrected = RGB_corrected.astype(int)

            # Asignar los nuevos valores de color al píxel
            adapted_pixels[x, y] = (int(R_corrected), int(G_corrected), int(B_corrected))

    # Guardar la imagen adaptada en el mismo path
    adapted_image.save(image_path)

#ALGORITMO PARA DICROMÁTICO------------------------------

def simulate_daltonism(image, type):
    if type == 'protanopia':
        matrix = np.array([[0.56667, 0.43333, 0.0],
                           [0.55833, 0.44167, 0.0],
                           [0.0, 0.24167, 0.75833]])
    elif type == 'deuteranopia':
        matrix = np.array([[0.625, 0.375, 0.0],
                           [0.7, 0.3, 0.0],
                           [0.0, 0.3, 0.7]])
    elif type == 'tritanopia':
        matrix = np.array([[0.95, 0.05, 0.0],
                           [0.0, 0.43333, 0.56667],
                           [0.0, 0.475, 0.525]])
    else:
        raise ValueError("Tipo de dicromatismo no reconocido")

    transformed_image = np.dot(image, matrix.T)
    transformed_image = np.clip(transformed_image, 0, 255)
    return transformed_image.astype(np.uint8)

def rgb_to_hsi(image):
    image = image.astype('float32') / 255.0
    r, g, b = cv2.split(image)
    intensity = (r + g + b) / 3.0

    min_rgb = np.minimum(np.minimum(r, g), b)
    saturation = 1 - min_rgb / (intensity + 1e-6)
    saturation[intensity == 0] = 0

    hue = np.zeros_like(r)
    mask = (saturation != 0)

    num = 0.5 * ((r - g) + (r - b))
    den = np.sqrt((r - g) ** 2 + (r - b) * (g - b) + 1e-6)
    theta = np.arccos(np.clip(num / den, -1, 1))

    hue[mask] = theta[mask]
    hue[b > g] = 2 * np.pi - hue[b > g]
    hue = hue / (2 * np.pi)

    return hue, saturation, intensity

def hsi_to_rgb(h, s, i):
    h = h * 2 * np.pi
    r, g, b = np.zeros_like(h), np.zeros_like(h), np.zeros_like(h)

    idx1 = (h < 2 * np.pi / 3)
    idx2 = (h >= 2 * np.pi / 3) & (h < 4 * np.pi / 3)
    idx3 = (h >= 4 * np.pi / 3)

    b[idx1] = i[idx1] * (1 - s[idx1])
    r[idx1] = i[idx1] * (1 + s[idx1] * np.cos(h[idx1]) / np.cos(np.pi / 3 - h[idx1]))
    g[idx1] = 3 * i[idx1] - (r[idx1] + b[idx1])

    h[idx2] = h[idx2] - 2 * np.pi / 3
    r[idx2] = i[idx2] * (1 - s[idx2])
    g[idx2] = i[idx2] * (1 + s[idx2] * np.cos(h[idx2]) / np.cos(np.pi / 3 - h[idx2]))
    b[idx2] = 3 * i[idx2] - (r[idx2] + g[idx2])

    h[idx3] = h[idx3] - 4 * np.pi / 3
    g[idx3] = i[idx3] * (1 - s[idx3])
    b[idx3] = i[idx3] * (1 + s[idx3] * np.cos(h[idx3]) / np.cos(np.pi / 3 - h[idx3]))
    r[idx3] = 3 * i[idx3] - (g[idx3] + b[idx3])

    rgb = cv2.merge((r, g, b))
    return np.clip(rgb * 255, 0, 255).astype('uint8')

def adjust_hsi(h, s, i):
    return h, s, i

def adapt_colors_for_dichromatic(image_path, type):
    # Cargar la imagen original
    original_image = Image.open(image_path).convert('RGB')
    image = np.array(original_image)

    # Simular daltonismo
    transformed_rgb = simulate_daltonism(image, type)
    h, s, i = rgb_to_hsi(transformed_rgb)
    h_prime, s_prime, i_prime = adjust_hsi(h, s, i)
    final_image = hsi_to_rgb(h_prime, s_prime, i_prime)
    final_image_pil = Image.fromarray(final_image)

    # Guardar la imagen adaptada en el mismo path
    final_image_pil.save(image_path)

#ALGORITMO PARA ACROMÁTICO------------------------


def rgb_to_grayscale_ntsc(image):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    gray_image = 0.299 * (image[:, :, 0] ** 2.2) + 0.587 * (image[:, :, 1] ** 2.2) + 0.114 * (image[:, :, 2] ** 2.2)
    gray_image = gray_image ** (1/2.2)
    return gray_image.astype(np.uint8)

def calculate_error(g, image_lab, color_clusters, range_c, range_t):
    L, a, b = cv2.split(image_lab)
    gray_image = g[0] * L + g[1] * a + g[2] * b
    
    error = 0
    for i in range(len(color_clusters)):
        for j in range(len(color_clusters)):
            if i != j:
                L_i, a_i, b_i = color_clusters[i]
                L_j, a_j, b_j = color_clusters[j]
                
                c_distance = np.sqrt((L_i - L_j) ** 2 + (a_i - a_j) ** 2 + (b_i - b_j) ** 2)
                t_distance = np.abs(g[0] * (L_i - L_j) + g[1] * (a_i - a_j) + g[2] * (b_i - b_j))
                
                error += (c_distance / range_c - t_distance / range_t) ** 2
    return error

def optimized_grayscale(image):
    image_lab = cv2.cvtColor(image, cv2.COLOR_BGR2Lab)
    L, a, b = cv2.split(image_lab)
    
    range_c = np.sqrt((L.max() - L.min()) ** 2 + (a.max() - a.min()) ** 2 + (b.max() - b.min()) ** 2)
    range_t = 255
    
    pixels = np.stack([L.flatten(), a.flatten(), b.flatten()], axis=1)
    kmeans = MiniBatchKMeans(n_clusters=100).fit(pixels)
    color_clusters = kmeans.cluster_centers_
    
    initial_g = [1, 0, 0]
    
    result = minimize(calculate_error, initial_g, args=(image_lab, color_clusters, range_c, range_t), method='CG', options={'maxiter': 10})
    optimized_g = result.x
    
    gray_image = optimized_g[0] * L + optimized_g[1] * a + optimized_g[2] * b
    gray_image = (gray_image - gray_image.min()) * (255 / (gray_image.max() - gray_image.min()))
    
    return gray_image.astype(np.uint8)

def adapt_colors_for_achromatic(image_path):
    image = cv2.imread(image_path)

    # Convertir la imagen a escala de grises optimizada
    optimized_gray_image = optimized_grayscale(image)
    optimized_gray_image_pil = Image.fromarray(optimized_gray_image)

    # Guardar la imagen adaptada en el mismo path
    optimized_gray_image_pil.save(image_path)



