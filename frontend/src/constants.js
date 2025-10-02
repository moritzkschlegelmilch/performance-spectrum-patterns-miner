export const NOT_CONFIGURED_ERROR = "invalid_metadata"
export const INVALID_EVENT_LOG_ERROR = "invalid_event_log"

export function formatHighestUnitTime(seconds) {
    // Time units: seconds, minutes, hours, days
    if (seconds >= 86400) {
        // 1 day = 86400 seconds
        const days = Math.floor(seconds / 86400);
        return `${days} day${days > 1 ? 's' : ''}`;
    } else if (seconds >= 3600) {
        // 1 hour = 3600 seconds
        const hours = Math.floor(seconds / 3600);
        return `${hours} hour${hours > 1 ? 's' : ''}`;
    } else if (seconds >= 60) {
        // 1 minute = 60 seconds
        const minutes = Math.floor(seconds / 60);
        return `${minutes} minute${minutes > 1 ? 's' : ''}`;
    } else {
        // Remaining seconds
        return `${seconds} second${seconds > 1 ? 's' : ''}`;
    }
}

export const CANVAS_BLUE = '#2B7FFFFF'

export const QUARTILE_COLORS = {
    BLUE: '#97c4f5',
    YELLOW: '#f8c600',
    ORANGE: '#e15600',
    RED: '#ff0606',
}

export const GLOBAL_CASE_FILTER = 'global'

export const PERFORMANCE_SPECTRUM_HEIGHT = 200;