<template>
  <div class="min-h-screen bg-gray-50">
    <section class="bg-gradient-to-br from-primary-600 via-primary-700 to-primary-800 text-white py-20">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center">
          <h1 class="text-4xl md:text-5xl font-bold mb-6">智能图像检测平台</h1>
          <p class="text-lg md:text-xl text-primary-100 mb-8 max-w-2xl mx-auto">
            基于先进的深度学习技术，提供精准、高效的图像检测服务，助力您的业务发展
          </p>
          <div class="flex flex-col sm:flex-row gap-4 justify-center">
            <button @click="$emit('navigate', 'detection')" class="bg-white text-primary-600 font-semibold px-8 py-3 rounded-lg hover:bg-gray-100 transition-colors shadow-lg">
              开始检测
            </button>
            <button @click="$emit('navigate', 'technology')" class="border-2 border-white text-white font-semibold px-8 py-3 rounded-lg hover:bg-white/10 transition-colors">
              了解技术
            </button>
          </div>
        </div>
      </div>
    </section>

    <section id="about" class="py-20 bg-white">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <h2 class="section-title text-center">项目介绍</h2>
        <div class="grid md:grid-cols-3 gap-8">
          <div v-for="feature in features" :key="feature.title" class="card text-center">
            <div class="w-16 h-16 mx-auto mb-4 bg-primary-100 rounded-xl flex items-center justify-center">
              <component :is="feature.icon" class="w-8 h-8 text-primary-600" />
            </div>
            <h3 class="text-xl font-semibold text-gray-800 mb-3">{{ feature.title }}</h3>
            <p class="text-gray-600">{{ feature.description }}</p>
          </div>
        </div>
      </div>
    </section>

    <section id="video" class="py-20 bg-gray-50">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <h2 class="section-title text-center">功能演示</h2>
        <div class="max-w-4xl mx-auto">
          <div class="bg-gray-900 rounded-2xl overflow-hidden shadow-2xl">
            <div class="aspect-video flex items-center justify-center">
              <div class="text-center text-white">
                <Play class="w-20 h-20 mx-auto mb-4 text-primary-400" />
                <p class="text-lg">功能演示视频</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section id="stats" class="py-20 bg-white">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <h2 class="section-title text-center">统计数据</h2>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-8">
          <div v-for="stat in stats" :key="stat.label" class="text-center">
            <div class="text-4xl md:text-5xl font-bold text-primary-600 mb-2">{{ stat.value }}</div>
            <div class="text-gray-600">{{ stat.label }}</div>
          </div>
        </div>
      </div>
    </section>

    <section id="quick-access" class="py-20 bg-gradient-to-br from-primary-50 to-primary-100">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <h2 class="section-title text-center">快速入口</h2>
        <div class="grid md:grid-cols-4 gap-6">
          <button 
            v-for="item in quickAccess" 
            :key="item.id"
            @click="$emit('navigate', item.navigate)"
            class="card text-center hover:-translate-y-1 cursor-pointer"
          >
            <div class="w-14 h-14 mx-auto mb-4 bg-primary-100 rounded-xl flex items-center justify-center">
              <component :is="item.icon" class="w-7 h-7 text-primary-600" />
            </div>
            <h3 class="font-semibold text-gray-800 mb-2">{{ item.title }}</h3>
            <p class="text-sm text-gray-500">{{ item.description }}</p>
          </button>
        </div>
      </div>
    </section>

    <footer class="bg-gray-800 text-white py-10">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center">
          <div class="flex items-center justify-center space-x-3 mb-4">
            <div class="w-8 h-8 bg-gradient-to-br from-primary-500 to-primary-700 rounded-lg flex items-center justify-center">
              <Eye class="w-5 h-5 text-white" />
            </div>
            <span class="text-lg font-bold">检测平台</span>
          </div>
          <p class="text-gray-400">© 2024 智能图像检测平台. All rights reserved.</p>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Eye, Zap, Shield, Layers, Play, Image, FileSearch, History, FileImage } from 'lucide-vue-next'

defineEmits(['navigate'])

const features = ref([
  { title: '精准检测', icon: Zap, description: '基于深度学习算法，提供高精度的图像检测服务' },
  { title: '安全可靠', icon: Shield, description: '严格的数据加密和隐私保护机制' },
  { title: '多场景支持', icon: Layers, description: '支持多种检测场景，满足不同业务需求' }
])

const stats = ref([
  { value: '100K+', label: '检测次数' },
  { value: '99.8%', label: '准确率' },
  { value: '50ms', label: '平均响应' },
  { value: '1000+', label: '企业用户' }
])

const quickAccess = ref([
  { id: 'single', title: '单图检测', description: '上传单张图片进行检测', icon: Image, navigate: 'detection' },
  { id: 'batch', title: '批量检测', description: '同时检测多张图片', icon: FileSearch, navigate: 'detection' },
  { id: 'history', title: '检测记录', description: '查看历史检测结果', icon: History, navigate: 'detection' },
  { id: 'large', title: '大图检测', description: '处理大尺寸图片', icon: FileImage, navigate: 'detection' }
])
</script>
