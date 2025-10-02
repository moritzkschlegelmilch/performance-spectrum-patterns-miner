import {computed, inject, ref, watch, provide} from "vue";
import {GLOBAL_CASE_FILTER} from "@/constants.js";
import {getLocalTimeZone} from "@internationalized/date";
import axios from "@/api/axios.js";
import {showInfo} from "@/composables/useErrorState.js";
import {useEventLogState} from "@/composables/useEventLogState.js";
import {CASE_FILTERS} from "@/caseFilters.js";
import {range} from "lodash";


const initState = () =>  {

    const configurationId = ref(null)
    // Loading variable to prevent spamming of requests
    const loadingConfiguration = ref(false)
    // True if there was an error loading the event log
    const errorLoading = ref(false)
    // Array of arrays of case filters that represents the history in which filters were applied to the spectrum
    const caseFilterHistory = ref([])
    // The model value for the date picker in the filter
    const dateModel = ref({
        start: null,
        end: null
    })

    // True if the event log is currently being exported
    const exportingLog = ref(false)

    // The model value for the segment picker in the filter
    const segmentModel = ref({
        start: null,
        end: null
    })
    // The model value for the clustering filter picker
    const clusteringModel = ref({
        enabled: false,
        batchType: null,
        epsilon: 10,
        minSamples: 20
    })
    // Id of the spectrum,i.e. the segment of a spectrum collection that is currently selected
    const currentSpectrum = ref(0)
    // Model of the quartile picker dropdown
    const quartilePickerModel = ref(null)

    // The data of the configuration, will be filled by the fetchConfiguration function
    const configurationData = ref(null)


    const {currentEventLogId} = useEventLogState()


    // Build a payload for the global filter that is used to export the event log
    const getGlobalFilterPayload = () => {
        const getFilterOfType = getFilterOfTypeForSpectrum(GLOBAL_CASE_FILTER)
        const cases = getFilterOfType(CASE_FILTERS.MANUAL)
        const variant = getFilterOfType(CASE_FILTERS.VARIANT)
        const {start, end} = getFilterOfType(CASE_FILTERS.DATERANGE) ?? {start: null, end: null}
        const time = {
            time_start: start?.toDate(getLocalTimeZone()),
            time_end: end?.toDate(getLocalTimeZone())
        }

        const {start: start_activity, end: end_activity} = getFilterOfType(CASE_FILTERS.SEGMENT) ?? {start: null, end: null}
        const activities = start_activity && end_activity ? {
            start_activity: start_activity.key,
            end_activity: end_activity.key
        } : {}

        return {
            cases,
            variant,
            activities,
            time
        }
    }

    // Create a payload for the spectrum with the given id
    const createSpectrumPayload = (spectrum) => {
        const getFilterOfType = getFilterOfTypeForSpectrum(spectrum)
        const quartile = getFilterOfType(CASE_FILTERS.QUARTILE)?.key
        const batches = getFilterOfType(CASE_FILTERS.CLUSTERING)

        return {
            on: spectrum,
            quartile,
            batches: {
                batchType: batches?.batchType.key,
                epsilon: batches?.epsilon,
                minSamples: batches?.minSamples
            }
        }
    }


    // Build the payload for the export or the fetching of the event log. They use the same logic.
    const buildFilterPayload = () => {

        const variantFilter = getFilterOfTypeForSpectrum(GLOBAL_CASE_FILTER)(CASE_FILTERS.VARIANT)
        // If there is no variant filter, we create a single spectrum payload with id 0, otherwise iterate over all
        // segments and create payload data for all of them.
        const spectra =  !variantFilter ?
            [createSpectrumPayload(0)] :
            range(0, variantFilter.length - 1).map(index => createSpectrumPayload(index))

        return {
            spectra,
            global_filters: getGlobalFilterPayload()
        }
    }

    const exportEventLog = () => {
        exportingLog.value = true
        const payload = buildFilterPayload()
        // Call the export endpoint of the event log. The exported log will then be stored on the server
        return axios.post(`/api/event-log/${currentEventLogId.value}/mined-data/export`, payload).then(
            ({data}) => {
                // Download the exported log
                axios.get(`/api/download/${data}`, {
                    responseType: 'blob',
                    headers: {
                        'Content-Type': 'application/zip'
                    }
                }).then((response) => {
                    const url = window.URL.createObjectURL(new Blob([response.data]))
                    const link = document.createElement('a')
                    link.href = url
                    link.setAttribute('download', data)
                    document.body.appendChild(link)
                    link.click()
                    exportingLog.value = false
                })
        })
    }

    const fetchConfiguration = () => {
        if (loadingConfiguration.value || errorLoading.value) return;
        loadingConfiguration.value = true

        // Gather payload automatically based on the current caseFilters
        const payload = buildFilterPayload()
        // Fetch the configuration spectrum
        return axios.post(`/api/event-log/${currentEventLogId.value}/mined-data`, payload).then(({data}) => {
            // Reset loading state
            configurationData.value = data
            loadingConfiguration.value = false
        }).catch((() => {
            errorLoading.value = true
        }))
    }

    // Eager load the configuration data
    const configuration = computed(() => {
        if (!configurationData.value) fetchConfiguration()
        return configurationData.value
    })

    // Return the most recent entry of the caseFilterHistory
    const currentFiltersForAllSpectra = computed(() => {
        if (!caseFilterHistory.value.length) return []
        return caseFilterHistory.value[caseFilterHistory.value.length - 1]
    })

    // Retrieve the current filters for a specific spectrum with the given id
    const getCurrentFiltersFor = (spectrum) => {
        return currentFiltersForAllSpectra.value[spectrum] || []
    }

    // Overwrites the global filters while dropping others. Used for global filters that invalidate segment filters
    // or other global ones.
    const overwriteGlobalFilters = (newFilters, keep = []) => {
        caseFilterHistory.value = [
            ...caseFilterHistory.value,
            {
                [GLOBAL_CASE_FILTER]:
                    [
                        // Keep the filters that are allowed to be kept by the function's parameter
                        ...getCurrentFiltersFor(GLOBAL_CASE_FILTER).filter(
                            (f) => keep.includes(f.type.id) && !newFilters.some(nf => f.type.id === nf.type.id)
                        ),
                        ...newFilters
                    ]
            }
        ]

    }

    // Mutate the current filters by adding new ones for a specific segment while creating a new history entry.
    const addCaseFilterHistoryEntryForSpectrum = (spectrum, entry, removeSpectrumFilters = false) => {
        const latestFilter = caseFilterHistory.value.length ?
            caseFilterHistory.value[caseFilterHistory.value.length - 1]
            : {}

        caseFilterHistory.value = [
            ...caseFilterHistory.value,
            {
                ...(removeSpectrumFilters ? {} : latestFilter),
                [spectrum]: entry
            }
        ]
    }

    // Get the filtered cases within a spectrum (will be the same for all segments of a variant)
    const getCasesOfSpectrum = (spectrum) => {
        return configuration.value.spectra[spectrum].records.map(item => item.case_ID)
    }

    const addCaseFilterForSpectrum = (spectrum, type, data) => {
        const newHistoryEntry = {
            type, data
        }

        // Some filters may delete others to prevent conflicts
        if (type.deleteFiltersExcept) {
            let caseFilter = []

            if (type.id !== CASE_FILTERS.MANUAL.id) {
                caseFilter.push({
                    type: CASE_FILTERS.MANUAL,
                    data: getCasesOfSpectrum(currentSpectrum.value)
                })
            }

            showInfo(`
                The filter that you selected invalidates other filters as they may conflict the logic of this filter.
                Therefore your filters were adjusted to select only cases selected before.
            `)
            // If the filter removes all other filters, we remove all filters for the spectrum
            overwriteGlobalFilters([newHistoryEntry, ...caseFilter], type.deleteFiltersExcept?.() ?? [])
            return
        }

        // Array of current case filters without the one to add (We want to replace it)
        const filteredFilters = getCurrentFiltersFor(spectrum).filter((f) => f.type.id !== type.id)
        addCaseFilterHistoryEntryForSpectrum(spectrum, [
            ...filteredFilters,
            newHistoryEntry
        ])
    }

    // Function to add a segment case filter
    const addCaseFilter = (type, data) => {
        addCaseFilterForSpectrum(currentSpectrum.value, type, data)
    }

    // Function to add a global case filter
    // Global filters are stored in the same data structure as regular segment filters,
    // the global spectrum id is stored as a constant
    const addGlobalCaseFilter = (type, data) => {
        addCaseFilterForSpectrum(GLOBAL_CASE_FILTER, type, data)
    }

    // Returns a function that retrieves the filter of a specific type for a given spectrum
    const getFilterOfTypeForSpectrum = (spectrum) => {
        return (type) => {
            const filters = getCurrentFiltersFor(spectrum)
            return filters.find((f) => f.type.id === type.id)?.data
        }
    }


    // Setter functions for filters

    const setFilteredCases = (caseIds) => {
        addGlobalCaseFilter(CASE_FILTERS.MANUAL, caseIds)
    }

    const setFilterDate = (date) => {
        // Sync the model value with the data value
        dateModel.value = date
        addGlobalCaseFilter(CASE_FILTERS.DATERANGE, date)
    }

    const setSegmentFilter = (start, end) => {
        // Sync the model value with the data value
        segmentModel.value = {start, end}
        addGlobalCaseFilter(CASE_FILTERS.SEGMENT, {start, end})
    }

    const setClusteringFilter = (batchType, epsilon, minSamples) => {
        // Sync the model value with the data value
        clusteringModel.value = {
            enabled: true,
            batchType,
            epsilon,
            minSamples
        }
        addCaseFilter(CASE_FILTERS.CLUSTERING, {batchType, epsilon, minSamples})
    }

    const setQuartileFilter = (quartile) => {
        // Sync the model value with the data value
        quartilePickerModel.value = quartile
        addCaseFilter(CASE_FILTERS.QUARTILE, quartile)
    }

    const setVariantFilter = (variant) => {
        // Scroll to top of page
        window.scrollTo({
            top: 200,
            behavior: 'smooth'
        });
        addGlobalCaseFilter(CASE_FILTERS.VARIANT, variant)
    }

    // Undo the last filter that was applied to the caseFilterHistory
    const undoFilter = () => {
        if (!caseFilterHistory.value.length) return;
        // Reset the spectrum to prevent undefined behaviour if going from a variant back for instance
        currentSpectrum.value = 0;
        // Pop the most recent history entry
        const popped = caseFilterHistory.value.pop()
        // Trigger a reactivity update by copying contents into a new array
        caseFilterHistory.value = [...caseFilterHistory.value]
        showInfo(
            'You have undone some of the given filters. You will not be able to recover this configuration directly'
        )
        return popped
    }

    // Map the segments of a variant into a list of segments with labels
    const getVariantSegments = (variant) => {
        const res = []
        for (let i = 0; i < variant.length - 1; i++){
            res.push({
                key: i,
                label: `${variant[i]} - ${variant[i + 1]}`,
            })
        }
        return res
    }

    return {
        configurationData,
        configurationId,
        loadingConfiguration,
        errorLoading,
        caseFilterHistory,
        dateModel,
        exportingLog,
        segmentModel,
        clusteringModel,
        quartilePickerModel,
        currentSpectrum,
        configuration,
        currentFiltersForAllSpectra,
        overwriteGlobalFilters,
        addCaseFilterHistoryEntryForSpectrum,
        fetchConfiguration,
        getCurrentFiltersFor,
        getVariantSegments,
        getFilterOfTypeForSpectrum,
        setVariantFilter,
        setQuartileFilter,
        setClusteringFilter,
        setSegmentFilter,
        setFilteredCases,
        setFilterDate,
        undoFilter,
        exportEventLog
    }
}

const stateSetup = (state) => {

    const {
        fetchConfiguration,
        caseFilterHistory,
        currentSpectrum,
        getCurrentFiltersFor,
        addCaseFilterHistoryEntryForSpectrum,
        overwriteGlobalFilters
    } = state

    // Function to remove a filter from the current spectrum
    const removeFilterFromSpectrum = (spectrum, filter) => {
        // If a global filter invalidates others, we overwrite the global filters except for the ones allowed to be kept
        if (filter.type.deleteFiltersExcept && filter.type.id !== CASE_FILTERS.MANUAL.id) {
            currentSpectrum.value = 0
            overwriteGlobalFilters([], filter.type.deleteFiltersExcept() ?? [])
            return
        }
        addCaseFilterHistoryEntryForSpectrum(spectrum,
            getCurrentFiltersFor(spectrum).filter((f) => f.type.id !== filter.type.id)
        )
        currentSpectrum.value = 0
    }

    // Call refresh callback on all case filters to sync the model values
    const refreshFilters = () => {
        for (let filter of Object.values(CASE_FILTERS)){
            filter.refresh?.(state)
        }
    }

    const updateFilters = () => {
        // Reset loading status
        fetchConfiguration()
        refreshFilters()
    }

    // When the caseFilterHistory changes, we update the filters or sync the models with current filter values
    watch(caseFilterHistory, updateFilters)
    watch(currentSpectrum, refreshFilters)

    return {
        removeFilterFromSpectrum
    }
}


// Storage of all configuration states
const configurations = {}
/*  Creates a new state object for a configuration. The two functions initState and stateSetup are used
    to create the initial state and setup the more complicated interactions, respectively. The state is then stored in
    the storage and can dynamically be loaded in components.
 */
export const createConfigurationState = () => {

    // Setup basic variables
    let state = initState()
    // Setup more complicated interactions.
    state = {
        ...state,
        ...stateSetup(state)
    }

    // Assign a valid id to resuse the state later
    const newId = Object.values(configurations).length ?
        Math.max(
            ...(
                Object.values(configurations).map((c) => c.configurationId.value)
            )
        ) + 1 : 1

    // Append the state to the storage
    configurations[newId] = state
    // Set the configuration id in the state, so it is aware of own identity.
    state.configurationId.value = newId

    return newId
}
/*
     Function called from components to mount the state of their current configuration.
     The parent component calls this function with the actual id of the configuration while child components
     just inject the id from the parent component and automatically choose the correct state.
 */
export const useConfigurationState = (configId = null) => {
    if (!configId) configId = inject('configurationId', null)
    provide('configurationId', configId)

    return configurations[configId]
}