import {GLOBAL_CASE_FILTER} from "@/constants.js";
import {formatter} from "@/composables/useEventLogState.js";


/*
    Array of case filter types used in the application. Each filter must provide an `id`, `name`, and a `displayData`
    function to format the data for display in the UI. Some filters may also provide a `deleteFiltersExcept` function,
    that returns an array of filter IDs that should not be deleted when this filter is removed. The `refresh` function
    is used to update the filter's data in the UI based on the current state of the application.
 */
export const CASE_FILTERS = {
    MANUAL: {
        id: 'manual',
        name: "Manual",
        deleteFiltersExcept(){
            return [CASE_FILTERS.DATERANGE.id, CASE_FILTERS.SEGMENT.id, CASE_FILTERS.VARIANT.id]
        },
        displayData(data){
            return `${data.length} cases selected`
        },
    },
    DATERANGE: {
        id: 'dateRange',
        name: "Date Range",
        displayData(data){
            return formatter.formatRange(data.start.toDate(), data.end.toDate())
        },
        refresh({dateModel, getFilterOfTypeForSpectrum}){
            const data = getFilterOfTypeForSpectrum(GLOBAL_CASE_FILTER)(CASE_FILTERS.DATERANGE)
            dateModel.value = data ?? {start: null, end: null}
        }
    },
    SEGMENT: {
        id: 'segment',
        name: "Segment filter",
        deleteFiltersExcept(){
            return [CASE_FILTERS.DATERANGE.id]
        },
        displayData({start, end}){
            return `${start.key} - ${end.key}`
        },
        refresh({segmentModel, getFilterOfTypeForSpectrum}){
            const segmentData = getFilterOfTypeForSpectrum(GLOBAL_CASE_FILTER)(CASE_FILTERS.SEGMENT)
            segmentModel.value = segmentData ?? {start: null, end: null}
        }
    },
    CLUSTERING: {
        id: 'clustering',
        name: "Batch Clustering",
        displayData({batchType, epsilon, minSamples}){
            return `Batch type: ${batchType.label}, Epsilon: ${epsilon}, Min samples: ${minSamples}`
        },
        refresh({clusteringModel, getFilterOfTypeForSpectrum, currentSpectrum}){
            const clusteringData = getFilterOfTypeForSpectrum(currentSpectrum.value)(CASE_FILTERS.CLUSTERING)
            if (clusteringData){
                clusteringData.enabled = true
            }
            clusteringModel.value = clusteringData ?? {enabled: false, batchType: null, epsilon: 10, minSamples: 20}
        }
    },
    QUARTILE: {
        id: 'quartile',
        name: "Quartile filter",
        displayData(quartile){
            return quartile.label
        },
        refresh({quartilePickerModel, getFilterOfTypeForSpectrum, currentSpectrum}){
            const quartileData = getFilterOfTypeForSpectrum(currentSpectrum.value)(CASE_FILTERS.QUARTILE)
            quartilePickerModel.value = quartileData ?? null
        }
    },
    VARIANT: {
        id: 'variant',
        name: "Variant filter",
        deleteFiltersExcept(){
            return [CASE_FILTERS.DATERANGE.id]
        },
        displayData(variant){
            return variant.reduce((acc, v) => {
                return `${acc} - ${v}`
            })
        }
    },
}