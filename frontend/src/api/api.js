import axios from "axios";

const api = axios.create({
    baseURL: "https://smellsenseai.onrender.com"
});

export default api;