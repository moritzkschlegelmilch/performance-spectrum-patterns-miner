import axios from "axios";
import {useErrorState} from "@/composables/useErrorState.js";
import router from "@/routes.js";
import {NOT_CONFIGURED_ERROR} from "@/constants.js";

const {showError} = useErrorState()
const axiosInstance = axios.create({
    baseURL: import.meta.env.VITE_BACKEND_ENDPOINT,
    timeout: 0,
    headers: {
        'Content-Type': 'application/json',
    },
});

axiosInstance.interceptors.response.use(
    response => response,
    error => {
        // Global error handling
        if (error.response) {
            if (error.response.status === 400 && error.response.data.detail.err === NOT_CONFIGURED_ERROR) {
                showError('Eventlog is not sufficiently configured')
                router.replace({name: 'ChooseFields', params: {id: error.response.data.detail.id}})
                return Promise.reject(error);
            } else if (error.response.status === 404) {
                showError('The requested resource was not found')
                router.replace({name: 'NotFound'})
            }
        }

        showError()
        return Promise.reject(error);
    }
);

export default axiosInstance