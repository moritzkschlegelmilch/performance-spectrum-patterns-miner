<template>
  <div class="w-full h-full min-h-0 items-center flex gap-15">
    <!-- left side -->
    <div>
      <img class="w-[280px] mb-10 mx-auto" src="/src/assets/undraw_upload_cucu.svg">
      <div class="text-3xl font-bold mb-3">Upload an event log.</div>
      <div class="text-gray-300 text-sm">To upload an event log, start by preparing the file in a supported format.
        Ensure the event log includes key columns such as Case ID, Activity, Timestamp, and any other relevant
        attributes. The Case ID should uniquely identify each process
        instance, the Activity Name should represent each action or step, the Timestamp should reflect when the activity
        occurred, and the Resource should specify who or what performed the action.
      </div>
    </div>
    <!-- end of left side -->

    <!-- right side -->
    <div class="flex flex-col gap-3">
      <!-- name input -->
      <div class="text-sm">Event log name</div>
      <Input v-model="nameInput" placeholder="Event-log name" @input="showInputError = false"></Input>
      <div v-if="formErrors.input" class="text-red-400 text-sm">{{ formErrors.input }}</div>
      <!-- end of name input -->

      <!-- file input -->
      <div class="text-sm">Event log file (XES format only)</div>
      <Card :class="{'border-blue-500': isOverDropZone}"
            class="w-[600px] ml-auto h-[300px] flex-shrink-0 border-dashed">
        <CardContent class="h-full">
          <div ref="dropZoneRef" class="w-full h-full min-h-0 z-10 flex flex-col items-center justify-center gap-4">

            <!-- hidden input to trigger file selection -->
            <input ref="inputRef" class="hidden" type="file" @change="onFileSelect($event.target?.files)"/>
            <template v-if="!file">
              <div class="flex gap-2">
                <Upload :class="isOverDropZone ? 'text-blue-500' : 'text-gray-400'" :size="22"/>
                <div :class="isOverDropZone ? 'text-blue-500' : 'text-gray-400'">Drag files here</div>
              </div>

              <Button variant="secondary" @click="triggerUploadInput">Upload file</Button>
            </template>
            <template v-else>
              <div class="flex gap-2">
                <FileCheck2 :size="22" class="text-blue-500"/>
                <div class="text-blue-500">{{ file.name }}</div>
              </div>
              <Button variant="secondary" @click="triggerUploadInput">Change file</Button>
            </template>
          </div>
        </CardContent>
      </Card>
      <div v-if="formErrors.dropZone" class="text-red-400 text-sm">{{ formErrors.dropZone }}</div>
      <!-- end of file input -->

      <Button :disabled="!file || loadingUpload" :loading="loadingUpload" @click="submitForm">
        <Loader2 v-if="loadingUpload" class="w-4 h-4 mr-2 animate-spin"/>
        Submit
      </Button>
    </div>
    <!-- end of right side -->
  </div>
</template>

<script lang="js" setup>

import Card from '../components/ui/card/Card.vue';
import CardContent from '../components/ui/card/CardContent.vue';
import {FileCheck2, Loader2, Upload} from "lucide-vue-next";

import {useDropZone} from '@vueuse/core'
import {computed, ref, useTemplateRef} from "vue";
import Button from "../components/ui/button/Button.vue";
import {Input} from '../components/ui/input';
import axios from '@/api/axios.js'
import {showError} from "@/composables/useErrorState.js";
import {useRouter} from "vue-router";


const dropZoneRef = useTemplateRef('dropZoneRef')
const inputRef = useTemplateRef('inputRef')

// Model of the event log name input
const nameInput = ref('')
// True iff there was an error with the file when submitting
const showFileError = ref(false)
const showInputError = ref(false)
// file object of event log to submit
const file = ref(null)

// Set a loading animation for the button when currently making an api request
const loadingUpload = ref(false)

// Computed property to control when errors are displayed in the form
const formErrors = computed(() => {
    let input = showInputError.value

    // Display an error if the enterd name length is not between 3 and 20 characters long
    if (nameInput.value.length) {
        if (nameInput.value.length > 20) {
            input = "Name must be at most 20 characters long"
        }
    }
    return {
        input,
        dropZone: showFileError.value
    }
})

// Callback when a file is selected
const onFileSelect = (files) => {
    if (files) {
        if (!files[0].name.endsWith('.xes')) {
            showFileError.value = "Please upload a file with the .xes extension"
            return
        }
        showFileError.value = false
        file.value = files[0]
    }
}

// Dummy function to trigger the file choosing dialog of the os
const triggerUploadInput = () => {
    inputRef.value?.click()
}

const router = useRouter()
// Api request to create an event log in the app based on the XES file
const saveEventLog = (name, file) => {
    // Set loading animation for the button
    loadingUpload.value = true
    const formData = new FormData();
    formData.append("file", file);
    formData.append("name", name);

    axios.post('/api/upload-event-log', formData, {
        headers: {
            'Content-Type': 'multipart/form-data'
        }
    }).then(({data}) => {
        // Redirect to choose fields page
        router.replace({
            name: 'ChooseFields',
            params: {id: data.id}
        })
    }).finally(() => {
        loadingUpload.value = false
    })
}

// Callback when submitting the form
const submitForm = () => {
    // We need to have a file uploaded to submit
    if (!file.value) {
        showFileError.value = "Please upload an event log"
        return
    }
    if (formErrors.value.input || !nameInput.value.length) {
        saveEventLog(removeExtension(file.value.name), file.value)
        return
    }

    saveEventLog(nameInput.value, file.value)
}

// Removes the extension of the filename to be passed
// as the new name of the event log on empty input
function removeExtension(filename) {
  return filename.slice(0, filename.lastIndexOf('.'));
}

// Init dropzone
const {isOverDropZone} = useDropZone(dropZoneRef, onFileSelect)
</script>