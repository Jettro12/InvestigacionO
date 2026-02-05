import axios from "axios";

const API_URL = "http://127.0.0.1:8000/api";  // Cambia esto si tu backend está en otro host

export const api = axios.create({
  baseURL: API_URL,
  headers: { "Content-Type": "application/json" },
});
