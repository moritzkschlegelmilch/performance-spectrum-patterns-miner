<template>
  <div class="h-full">
    <!-- page layout -->
    <div v-if="!eventLog?.timestamp || step < 4">
      <choose-fields-stepper :step="step" :steps="steps"></choose-fields-stepper>
      <div class="mt-15">
        <!-- main selection section -->
        <template v-if="!loadingEventLog && eventLog">
          <div class="flex justify-start items-center">
            <div>
              <div class="text-2xl font-bold">{{ steps[step - 1].title }}</div>
              <div class="text-gray-500">for event log {{ eventLog.name }}</div>
            </div>
            <Button class="ml-auto" variant="secondary" @click="resetSelection">Reset selection</Button>
          </div>
          <Separator class="my-3"></Separator>
          <fields-table :data="tabularLogData" :exclude="[eventLog.activity, eventLog.case_id, eventLog.timestamp]"
                        @choose-col="chooseColumn"
          ></fields-table>
        </template>

        <!-- skeleton loaders -->
        <template v-else>
          <div class="flex justify-center">
            <div class="flex flex-col items-center">
              <div class="text-2xl text-center font-bold">Loading event log</div>
              <div class="text-gray-500">Patience is a virtue. This may take a few minutes.</div>
              <Loader2 :size="40" class="animate-spin mt-4"/>
            </div>
            <div></div>
          </div>
          <div class="divide-y divide-gray-100 mt-10">
            <div
              v-for="i in 10"
              :key="i"
              class="grid grid-cols-5 gap-4 py-4 items-center"
            >
              <div class="h-4 w-full bg-gray-200 rounded animate-pulse"></div>
              <div class="h-4 w-full bg-gray-200 rounded animate-pulse"></div>
              <div class="h-4 w-full bg-gray-200 rounded animate-pulse"></div>
              <div class="h-4 w-full bg-gray-200 rounded animate-pulse"></div>
              <div class="h-4 w-full bg-gray-200 rounded animate-pulse"></div>
            </div>
          </div>
        </template>
        <!-- end of skeleton loaders -->
      </div>
    </div>
    <div v-else class="flex w-full h-full justify-center items-center gap-20">
      <img class="w-[300px]" src="../assets/undraw_done_i0ak.svg">
      <div class="flex-col">
        <div class="text-2xl font-bold">Successful!</div>
        <div class="text-gray-500">You have successfull uploaded your event log</div>
        <RouterLink :to="{name: 'EventLogDetails', params: {id: eventLog.id}}">
          <Button class="mt-4">
            <Play v-if="!loadingEventLogColumns"></Play>
            <Loader2 v-else class="animate-spin"></Loader2>
            Analyze performance spectrum
          </Button>
        </RouterLink>
      </div>
    </div>
    <!-- end of page layout -->
    <AlertDialog v-model:open="alertDialogModel">
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle class="text-red-500">Your event log is faulty</AlertDialogTitle>
          <AlertDialogDescription>
            This action cannot be undone. This will permanently delete your account
            and remove your data from our servers.
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <Button variant="secondary" @click="routeToAllLogs">To overview</Button>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  </div>
</template>

<script lang="js" setup>
import ChooseFieldsStepper from "../components/ChooseFields/ChooseFieldsStepper.vue";
import {computed, ref} from "vue";
import axios from "../api/axios.js";
import {Loader2, Play} from "lucide-vue-next";
import FieldsTable from "../components/ChooseFields/FieldsTable.vue";
import Button from "@/components/ui/button/Button.vue";
import {showError} from "@/composables/useErrorState.js";
import {
    AlertDialog,
    AlertDialogAction,
    AlertDialogCancel,
    AlertDialogContent,
    AlertDialogDescription,
    AlertDialogFooter,
    AlertDialogHeader,
    AlertDialogTitle,
} from '@/components/ui/alert-dialog'
import Separator from "@/components/ui/separator/Separator.vue";

const props = defineProps({
    id: {
        type: Number,
        default: -1
    }
})

const routeToAllLogs = () => {
    // Navigate to the overview of all event logs
    window.location.href = '/event-logs'
}

// Model to control the visibility of the alert dialog
const alertDialogModel = ref(false)

// Array of steps in the stepper
const steps = [
    {
        step: 1,
        title: 'Upload files',
        description: 'Provide your name and XES-log',
        completed: true
    },
    {
        step: 2,
        title: 'Choose Case ID',
        column: 'case_id',
        description: 'Specify event log data',
    },
    {
        step: 3,
        title: 'Choose Activity column',
        column: 'activity',
        description: 'Specify event log data',
    },
    {
        step: 4,
        title: 'Choose timestamp',
        column: 'timestamp',
        description: 'Specify event log data',
    }
]

/**
 * Compute the current step in the stepper based on the columns we have already set in the event log
 */
const step = computed(() => {
    if (!eventLog.value) return;

    if (eventLog.value.activity && eventLog.value.case_id) {
        return 4
    }

    if (eventLog.value.case_id) {
        return 3
    }

    return 2
})

const loadingEventLog = ref(true)
const eventLog = ref(null)
const tabularLogData = ref([])
const loadingEventLogColumns = ref(false)

/**
 * Fetch event log data from the app once the component is being mounted
 */
axios.get(`/api/event-log/basic/${props.id}`).then(({data}) => {
    eventLog.value = data.event_log
    tabularLogData.value = data.df
}).catch(() => {
  alertDialogModel.value = true
}).finally(() => {
    loadingEventLog.value = false
})

/**
 * Save selected columns to database
 */
const commitEventLogData = () => {
    loadingEventLogColumns.value = true
    axios.post(`/api/commit-event-log/${eventLog.value.id}`, eventLog.value).catch(() => showError()).finally(() => {
        loadingEventLogColumns.value = false
    })
}

/**
 * Set the column for the current column to be selected
 */
const chooseColumn = (col) => {
    if (!eventLog.value) return;
    const currentStepColumn = steps[step.value - 1].column;
    eventLog.value[currentStepColumn] = col;

    // If all columns were set, i.e. the last step was completed, send the data to the app
    if (eventLog.value.case_id && eventLog.value.activity && eventLog.value.timestamp) {
        commitEventLogData()
    }
}

/**
 * Reset the selectable columns in case the user made a mistake
 */
const resetSelection = () => {
    eventLog.value.activity = null
    eventLog.value.case_id = null
    eventLog.value.timestamp = null
}
</script>