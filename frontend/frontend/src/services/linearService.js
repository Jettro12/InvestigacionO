import { api } from "./api";

export const solveLinear = async (data) => {
  try {
    const response = await api.post("/solve_linear", data);
    return response.data;  // Retorna los datos de la respuesta si la solicitud fue exitosa.
  } catch (error) {
    // Manejo de error más completo
    if (error.response) {
      // El servidor respondió con un código de error
      const backendDetail = error.response.data.detail;
      // Si el backend devuelve un array de errores, únelos en un solo string
      if (Array.isArray(backendDetail)) {
        throw new Error(backendDetail.join(" "));
      }
      throw new Error(backendDetail || error.response.data.message || "Error desconocido en el servidor.");
    } else if (error.request) {
      // No se recibió respuesta del servidor
      console.error("No se recibió respuesta del servidor:", error.request);
      throw new Error("No se recibió respuesta del servidor. Intenta nuevamente.");
    } else {
      // Otro tipo de error (por ejemplo, errores de configuración)
      console.error("Error al configurar la solicitud:", error.message);
      throw new Error("Error al configurar la solicitud. Intenta nuevamente.");
    }
  }
};