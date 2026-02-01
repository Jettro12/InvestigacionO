import axios from "axios";

export const solveNetwork = async (data) => {
  try {
    const response = await axios.post("http://127.0.0.1:8000/api/solve_network", data);

    return response.data;
  } catch (error) {
    console.error("Error al resolver optimización en redes:", error.response?.data || error.message);
    return null;
  }
};
