<template>
  <div>
    <div class="flex-col flex gap-1">
      <div class="text-2xl font-bold">All event logs</div>
      <div class="text-sm text-gray-500 w-[400px]">This page displays all saved event logs. If you wish to upload a new
        one, just
        click the button below.
      </div>
      <div class="flex gap-2 mt-4">
        <router-link to="/upload">
          <Button variant="secondary">Upload</Button>
        </router-link>
        <a href="https://multiprocessmining.org/2020/10/06/the-performance-spectrum/" target="_blank" title="Read more about the performance spectrum"
           rel="noopener noreferrer">
          <Button variant="text">Read more</Button>
        </a>
      </div>
    </div>
    <Separator class="my-8" label="Event logs"/>
    <div class="grid grid-cols-[repeat(auto-fill,_minmax(250px,_1fr))] gap-3">

      <!-- Delete alert dialog -->
      <AlertDialog
        v-model:open="showDeleteConfirmModal"
        :title="'Are you absolutely sure?'"
        :description="'This action cannot be undone. This will permanently delete your event log.'"
      >
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Are you absolutely sure?</AlertDialogTitle>
            <AlertDialogDescription>
              This action cannot be undone. This will permanently delete this eventlog.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <Button variant="destructive" @click="deleteEventLog(); showDeleteConfirmModal = false">Continue</Button>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
      <!-- End of delete alert dialog -->

      <router-link v-for="eventLog in eventLogs" :key="eventLog.id"
                   :to="{name: 'EventLogDetails', params: {id: eventLog.id}}" >
        <Card class="p-0">
          <CardContent class="p-5 h-[180px] flex flex-col">
            <div class="flex gap-2">
              <div class="w-full overflow-hidden">
                <div class="text-xs text-gray-500">Event log</div>
                <div class="text-lg font-bold text-ellipsis overflow-hidden w-full truncate">{{ eventLog.name }}</div>
              </div>
              <Trash :size="18" @click.stop.prevent="openDeleteModal(eventLog.id)" class="ml-auto text-gray-500"/>
              <Logs :size="18"/>
            </div>
            <template v-if="eventLog.entry_count">
              <div class="flex gap-2 items-center mt-2">
                <div class="dot"></div>
                <div class="text-sm text-gray-500"><span class="text-white">{{ eventLog.entry_count }}</span> rows</div>
              </div>

              <div class="flex gap-2 items-center mt-1">
                <div class="dot"></div>
                <div class="text-sm text-gray-500"><span class="text-white">{{ eventLog.column_count }}</span> columns
                </div>
              </div>

            </template>
            <template v-else>
              <div class="flex gap-2 items-center mt-2">
                <CircleAlert class="text-red-500" :size="16"/>
                <div class="text-red-500 text-xs">Event log may be faulty.</div>
              </div>
            </template>

            <div class="mt-auto text-xs text-blue-500">Click to view</div>
          </CardContent>
        </Card>
      </router-link>
    </div>
  </div>
</template>

<script lang="js" setup>
import axios from "@/api/axios.js";
import {ref} from "vue";
import {Button} from "@/components/ui/button";
import {Separator} from '@/components/ui/separator'
import Card from "@/components/ui/card/Card.vue";
import CardContent from "@/components/ui/card/CardContent.vue";
import {Logs, CircleAlert, Trash} from "lucide-vue-next";
import {
    AlertDialog,
    AlertDialogContent,
    AlertDialogHeader,
    AlertDialogTitle,
    AlertDialogDescription,
    AlertDialogFooter,
    AlertDialogCancel,
} from '@/components/ui/alert-dialog';



const loadingEventLogs = ref(true)
const showDeleteConfirmModal = ref(false); // Controls visibility of the modal
const eventLogToDelete = ref(null); // Stores the event log to be deleted
const eventLogs = ref([])

// Fetch all event logs from the API while component is mounting
axios.get(`/api/event-logs/`).then(({data}) => {
    eventLogs.value = data
}).finally(() => {
    loadingEventLogs.value = false
})


// Open the delete confirmation modal
const openDeleteModal = (eventLog) => {
    eventLogToDelete.value = eventLog; // Store the event log to be deleted
    showDeleteConfirmModal.value = true; // Show the modal
}

const deleteEventLog = () => {
    axios.delete(`/api/delete-event-log/${eventLogToDelete.value}`).then(() => {
        // Remove the deleted event log from the list
        eventLogs.value = eventLogs.value.filter(eventLog => eventLog.id !== eventLogToDelete.value);
    })
}
</script>

<style lang="scss" scoped>

</style>