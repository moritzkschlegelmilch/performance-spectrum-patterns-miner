import {createRouter, createWebHistory} from 'vue-router'
import HomeView from './views/HomeView.vue'
import UploadView from './views/UploadView.vue'
import ChooseFieldsView from "./views/ChooseFieldsView.vue"
import PerformanceSpectrumView from "@/views/PerformanceSpectrumView.vue";
import PerformanceSpectrumOverviewWrapper from "@/views/PerformanceSpectrumOverviewWrapper.vue";
import AllSpectrumsView from "@/views/AllEventLogs.vue";
import NotFoundView from "@/views/NotFoundView.vue";

const routes = [
    {
        path: '/',
        name: 'Home',
        component: HomeView
    },
    {
        path: '/upload',
        name: 'Upload',
        children: [
            {
                path: '',
                component: UploadView,
            },
            {
                path: 'choose-fields/:id',
                name: 'ChooseFields',
                component: ChooseFieldsView,
                props: route => ({id: +route.params.id})
            }
        ]
    },
    {
        path: '/event-logs',
        children: [
            {
                path: '',
                component: AllSpectrumsView,
                name: "AllSpectrums",
            },
            {
                path: ':id',
                component: PerformanceSpectrumOverviewWrapper,
                props: route => ({id: +route.params.id}),
                children: [
                    {
                        path: '',
                        name: 'EventLogDetails',
                        component: PerformanceSpectrumView
                    }
                ]
            },
        ]
    },
    {
        path: '/:pathMatch(.*)*',
        name: "NotFound",
        component: NotFoundView,
    },
]

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes
})

export default router
