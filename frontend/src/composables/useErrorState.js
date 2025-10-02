import {reactive, ref} from "vue";
import {debounce} from "lodash";

const error = reactive({text: '', display: false, color: '', title: ''});
const hideError = () => {
    error.display = false;
}
const debounceHideError = debounce(hideError, 5000);

export const showError = (text = 'An unexpected error occurred. We recommend you completely refreshing your page.', options = {}) => {
    error.title = options.title ?? 'An Error occurred';
    error.text = text;
    error.display = true;
    error.color = options.color ?? 'text-red-500';
    debounceHideError();
}


export const showInfo = (text = 'Information.', options = {}) => {
    error.title = options.title ?? 'Info';
    error.text = text;
    error.display = true;
    error.color = options.color ?? 'text-blue-500';
    debounceHideError();
}

export const useErrorState = () => {
    return {error, showError}
}