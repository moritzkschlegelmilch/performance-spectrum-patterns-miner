<template>
  <div
    @mouseleave="onMouseLeave"
    @mousedown="onMouseDown"
    ref="wrapper"
    class="relative overflow-visible rounded-xl"
  >
    <div class="bg-black z-10 opacity-30 absolute top-0 w-20 h-20" :style="selectionRectangleDimensions"></div>
    <slot></slot>
  </div>
</template>

<script setup lang="js">
import {ref, provide, computed, onMounted, onUnmounted} from "vue";
// Current coordinates of the mouse pointer, used to compute the selection rectangle
const currentCoords = ref({left: 0, top: 0})
// Starting coordinates of the mouse pointer when the selection of the rectangle starts
const startingCoords = ref({left: 0, top: 0})
// Whether the rectangle selection is currently active (i.e., the mouse is pressed down and moving)
const hovering = ref(false)
// Html element that contains the selection rectangle
const wrapper = ref(null)

const emit = defineEmits(['selected'])

const getCoordsRelativeToContainer = (clientX, clientY) => {
    const containerRect = wrapper.value.getBoundingClientRect();
    const mouseX = clientX - containerRect.left; // Mouse x position relative to container
    const mouseY = clientY - containerRect.top; // Mouse y position relative to container
    return {
        mouseX, mouseY
    }
}

onMounted(() => {
    document.addEventListener('mousemove', onMouseMove)
    document.addEventListener('mouseup', onMouseUp)
})

onUnmounted(() => {
    document.removeEventListener('mousemove', onMouseMove)
})

const selectionRectangleDimensions = computed( () => {
    if (!hovering.value) return {
        display: 'none'
    }

    const top = Math.min(currentCoords.value.top, startingCoords.value.top) + 'px'
    const left = Math.min(currentCoords.value.left, startingCoords.value.left) + 'px'

    const width = Math.abs(currentCoords.value.left - startingCoords.value.left) + 'px'
    const height = Math.abs(currentCoords.value.top - startingCoords.value.top) + 'px'

    return {
        top, left, width, height
    }
})

const onMouseMove = (event) => {
    const {mouseX, mouseY} = getCoordsRelativeToContainer(event.clientX, event.clientY)
    currentCoords.value = {
        left: mouseX,
        top: mouseY
    }
}

const onMouseDown = (event) => {
    const {mouseX, mouseY} = getCoordsRelativeToContainer(event.clientX, event.clientY)
    startingCoords.value = {
        left: mouseX,
        top: mouseY
    }
    hovering.value = true
}

const onMouseUp = () => {
    const hovered = hovering.value
    hovering.value = false

    if (!wrapper.value || !hovered) return;

    const rect = wrapper.value.getBoundingClientRect()
    const start = Math.min(currentCoords.value.left, startingCoords.value.left) / rect.width
    const end = Math.max(currentCoords.value.left, startingCoords.value.left) / rect.width

    if ((end - start) > 0.01) emit('selected', {start, end})
}

const onMouseLeave = () => {
    if (hoveredCases.value.length){
        hoveredCases.value = []
    }
}

const hoveredCases = ref([])

provide('rectangleSelectActive', hovering)
provide('hoveredCases', hoveredCases)
</script>

<style scoped lang="scss">

</style>