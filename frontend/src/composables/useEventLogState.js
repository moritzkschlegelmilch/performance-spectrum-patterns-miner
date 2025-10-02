import {computed, ref} from "vue";
import axios from "@/api/axios.js";
import {GLOBAL_CASE_FILTER} from "@/constants.js";
import {createConfigurationState} from "@/composables/useConfigurationState.js";

// Batching types for clustering
export const BATCH_TYPES = [
    {label: 'Batching on start', key: 'start'},
    {label: 'Batching on end', key: 'end'},
    {label: 'Batching on both ends', key: 'both'}
]

// Datetime formatter global object
export const formatter = new Intl.DateTimeFormat('de-DE', {
    day: 'numeric',
    month: 'long',
    year: 'numeric'
});


const eventLogData = ref({})
const currentEventLogId = ref(null)
const loadingEventLogData = ref(false)


const fetchEventLog = (logId) => {
    loadingEventLogData.value = true
    return axios.get(`/api/event-log/${logId}/data`).then(({data}) => {

        const basicConfigurationId = createConfigurationState()
        eventLogData.value[logId] = {
            ...data,
            configurations: [{
                name: 'Default',
                id: basicConfigurationId,
            }],
            sideBySideConfigurations: [basicConfigurationId],
            currentConfiguration: basicConfigurationId,
        }
    }).finally(() => {
        loadingEventLogData.value = false
    })
}

// Eager load event logs
const currentEventLog = computed(() => {
    if (!eventLogData.value[currentEventLogId.value] && currentEventLogId.value > 0) {
        fetchEventLog(currentEventLogId.value)
    }
    return eventLogData.value[currentEventLogId.value]
})

// Called by the user to set the event log currently displayed
const loadEventLog = (logId) => {
    currentEventLogId.value = logId
}

const deleteConfiguration = (configurationId) => {
    const eventLog = eventLogData.value[currentEventLogId.value]
    eventLog.sideBySideConfigurations = eventLog.sideBySideConfigurations.filter((c) => c !== configurationId)

    eventLog.configurations = eventLog.configurations.filter((c) => c.id !== configurationId)

    eventLog.currentConfiguration = eventLog.sideBySideConfigurations[0]
}

const setConfigurationView = (index, id) => {
    const eventLog = eventLogData.value[currentEventLogId.value]
    eventLog.sideBySideConfigurations[index] = id
    eventLog.currentConfiguration = id
}

const addConfiguration = (name) => {
    const config = {
        name,
        id: createConfigurationState(),
    }
    eventLogData.value[currentEventLogId.value].configurations.push(config)

    if (!inSideBySideView.value){
        setConfigurationView(1, config.id)
    }
}

const selectedConfiguration = computed(() => {
    const eventLog = eventLogData.value[currentEventLogId.value]
    if (eventLog) {
        return eventLog.configurations.find((c) => c.id === eventLog.currentConfiguration)
    }
    return null
})


const inSideBySideView = computed(() => {
    return currentEventLog.value.sideBySideConfigurations.length > 1
})

const switchView = () => {

    const index = currentEventLog.value.sideBySideConfigurations.findIndex(
        (c) => c === currentEventLog.value.currentConfiguration
    )

    eventLogData.value[currentEventLogId.value].currentConfiguration = currentEventLog.value.sideBySideConfigurations[1 - index]
}

export const useEventLogState = () => {
    return {
        currentEventLog,
        currentEventLogId,
        loadingEventLogData,
        inSideBySideView,
        selectedConfiguration,
        switchView,
        setConfigurationView,
        deleteConfiguration,
        loadEventLog,
        addConfiguration
    }
}