<template>
  <AlertDialog :open="open" @update:open="updateOpen">
    <AlertDialogTrigger as-child>
      <slot name="trigger"></slot>
    </AlertDialogTrigger>
    <AlertDialogContent>
      <AlertDialogHeader>
        <AlertDialogTitle>{{ title }}</AlertDialogTitle>
        <AlertDialogDescription>{{ description }}</AlertDialogDescription>
      </AlertDialogHeader>
      <AlertDialogFooter>
        <AlertDialogCancel @click="cancelAction">Cancel</AlertDialogCancel>
        <AlertDialogAction @click="confirmAction">Continue</AlertDialogAction>
      </AlertDialogFooter>
    </AlertDialogContent>
  </AlertDialog>
</template>

<script setup lang="ts">
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '@/components/ui/alert-dialog'

const props = defineProps({
  open: Boolean,
  title: String,
  description: String,
  onConfirm: Function,
})

const emit = defineEmits()

const cancelAction = () => {
  emit('update:open', false)
}

const confirmAction = () => {
  if (typeof props.onConfirm === 'function') {
    props.onConfirm()
  }
  emit('update:open', false)
}

const updateOpen = (newOpenValue: boolean) => {
  emit('update:open', newOpenValue)
}
</script>