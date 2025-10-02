<template>
  <div class="flex flex-col h-screen">
    <!-- Global error alert -->
    <Alert class="fixed bottom-0 right-0 mr-5 mb-5 w-[500px] flex gap-2 z-20" v-if="error.display" :class="error.color">
      <CircleAlert :class="error.color" class="flex-shrink-0"/>
      <div>
        <AlertTitle :class="error.color">{{error.title}}</AlertTitle>
        <AlertDescription>
          {{error.text}}
        </AlertDescription>
      </div>
    </Alert>

    <!-- End of global error alert -->
    <nav-bar></nav-bar>
    <!-- General page container -->
    <div class="max-w-7xl px-6 mx-auto mt-10 w-full min-h-0 h-full flex flex-col">
      <router-view></router-view>
    </div>
    <!-- End of General page container -->
  </div>
</template>

<script lang="js" setup>
import NavBar from "./components/root/NavBar.vue";
import { CircleAlert } from 'lucide-vue-next';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import {useErrorState} from "@/composables/useErrorState.js";

const {error} = useErrorState()
</script>