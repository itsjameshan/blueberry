<script setup>
import { ref } from 'vue'
import NavBar from './components/NavBar.vue'
import HomePage from './components/HomePage.vue'
import TechnologyPage from './components/TechnologyPage.vue'
import DetectionPage from './components/DetectionPage.vue'

const currentPage = ref('home')

const handleNavigate = (pageId) => {
  currentPage.value = pageId
  window.scrollTo({ top: 0, behavior: 'smooth' })
}
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <NavBar :currentPage="currentPage" @navigate="handleNavigate" />
    <main>
      <HomePage v-if="currentPage === 'home'" @navigate="handleNavigate" />
      <TechnologyPage v-else-if="currentPage === 'technology'" />
      <DetectionPage v-else-if="currentPage === 'detection'" />
    </main>
  </div>
</template>

<style scoped>
</style>
