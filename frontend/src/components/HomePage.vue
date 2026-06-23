<template>
  <div class="min-h-screen bg-gray-50">
    <section class="pt-48 pb-8">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="relative">
          <div class="aspect-video bg-gray-900 rounded-2xl overflow-hidden">
            <img 
              :src="slides[currentSlide].image" 
              :alt="slides[currentSlide].title"
              class="w-full h-full object-cover"
            />
            <div class="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent"></div>
            <div class="absolute bottom-6 left-6 right-6">
              <h2 class="text-2xl font-bold text-white mb-2">{{ slides[currentSlide].title }}</h2>
              <p class="text-gray-200">{{ slides[currentSlide].description }}</p>
            </div>
          </div>
          <button 
            @click="prevSlide" 
            class="absolute left-4 top-1/2 -translate-y-1/2 w-10 h-10 bg-white/20 hover:bg-white/40 rounded-full flex items-center justify-center text-white transition-colors"
          >
            <ChevronLeft class="w-6 h-6" />
          </button>
          <button 
            @click="nextSlide" 
            class="absolute right-4 top-1/2 -translate-y-1/2 w-10 h-10 bg-white/20 hover:bg-white/40 rounded-full flex items-center justify-center text-white transition-colors"
          >
            <ChevronRight class="w-6 h-6" />
          </button>
          <div class="absolute bottom-3 left-1/2 -translate-x-1/2 flex space-x-2">
            <button 
              v-for="(slide, index) in slides" 
              :key="index"
              @click="currentSlide = index"
              :class="[
                'w-3 h-3 rounded-full transition-colors',
                currentSlide === index ? 'bg-white' : 'bg-white/50'
              ]"
            ></button>
          </div>
        </div>
      </div>
    </section>

    <section class="py-12 bg-white">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="grid md:grid-cols-2 gap-8">
          <div>
            <div class="flex items-center justify-between mb-6">
              <h2 class="text-xl font-bold text-gray-800 border-b-2 border-green-600 pb-2">学院新闻</h2>
              <button class="text-green-600 hover:text-green-700 text-sm">更多 >></button>
            </div>
            <div class="space-y-4">
              <div v-for="news in newsList" :key="news.id" class="flex gap-4">
                <img :src="news.image" class="w-24 h-16 object-cover rounded-lg" />
                <div>
                  <h3 class="font-medium text-gray-800 hover:text-green-600 cursor-pointer">{{ news.title }}</h3>
                  <p class="text-sm text-gray-500">{{ news.summary }}</p>
                </div>
              </div>
            </div>
          </div>
          
          <div>
            <div class="flex items-center justify-between mb-6">
              <h2 class="text-xl font-bold text-gray-800 border-b-2 border-green-600 pb-2">通知公告</h2>
              <button class="text-green-600 hover:text-green-700 text-sm">更多 >></button>
            </div>
            <div class="space-y-3">
              <div v-for="notice in notices" :key="notice.id" class="flex gap-4 p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors cursor-pointer">
                <div class="text-center">
                  <div class="bg-green-600 text-white text-lg font-bold px-3 py-1 rounded">{{ notice.day }}</div>
                  <div class="text-gray-500 text-sm">{{ notice.date }}</div>
                </div>
                <div class="flex-1">
                  <h3 class="font-medium text-gray-800">{{ notice.title }}</h3>
                  <p class="text-sm text-gray-500">{{ notice.summary }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section id="about" class="py-12 bg-green-50">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <h2 class="section-title text-center">项目介绍</h2>
        <div class="grid md:grid-cols-3 gap-8">
          <div v-for="feature in features" :key="feature.title" class="card text-center">
            <div class="w-16 h-16 mx-auto mb-4 bg-green-100 rounded-xl flex items-center justify-center">
              <component :is="feature.icon" class="w-8 h-8 text-green-600" />
            </div>
            <h3 class="text-xl font-semibold text-gray-800 mb-3">{{ feature.title }}</h3>
            <p class="text-gray-600">{{ feature.description }}</p>
          </div>
        </div>
      </div>
    </section>

    <section id="stats" class="py-12 bg-white">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <h2 class="section-title text-center">统计数据</h2>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-8">
          <div v-for="stat in stats" :key="stat.label" class="text-center">
            <div class="text-4xl md:text-5xl font-bold text-green-600 mb-2">{{ stat.value }}</div>
            <div class="text-gray-600">{{ stat.label }}</div>
          </div>
        </div>
      </div>
    </section>

    <section id="quick-access" class="py-12 bg-gradient-to-br from-green-50 to-green-100">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <h2 class="section-title text-center">快速入口</h2>
        <div class="grid md:grid-cols-4 gap-6">
          <button 
            v-for="item in quickAccess" 
            :key="item.id"
            @click="$emit('navigate', item.navigate)"
            class="card text-center hover:-translate-y-1 cursor-pointer"
          >
            <div class="w-14 h-14 mx-auto mb-4 bg-green-100 rounded-xl flex items-center justify-center">
              <component :is="item.icon" class="w-7 h-7 text-green-600" />
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
            <div class="w-8 h-8 bg-green-600 rounded-lg flex items-center justify-center">
              <GraduationCap class="w-5 h-5 text-white" />
            </div>
            <span class="text-lg font-bold">昆明学院 · 智慧农业1班</span>
          </div>
          <p class="text-gray-400">© 2024 昆明学院智慧农业1班 - 图像检测系统. All rights reserved.</p>
          <p class="text-gray-500 text-sm mt-2">指导老师：XXX | 项目负责人：XXX</p>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { GraduationCap, Zap, Shield, Layers, Image, FileSearch, History, FileImage, ChevronLeft, ChevronRight } from 'lucide-vue-next'

defineEmits(['navigate'])

const currentSlide = ref(0)

const slides = ref([
  { 
    image: 'https://picsum.photos/1200/400?random=1', 
    title: '智慧农业技术创新',
    description: '利用先进的图像识别技术，助力现代农业发展'
  },
  { 
    image: 'https://picsum.photos/1200/400?random=2', 
    title: '农业病虫害检测',
    description: '精准识别农作物病虫害，保障农产品质量安全'
  },
  { 
    image: 'https://picsum.photos/1200/400?random=3', 
    title: '昆明学院智慧农业1班',
    description: '致力于农业智能化技术研究与实践'
  }
])

const newsList = ref([
  { id: 1, title: '智慧农业1班项目成果展示', summary: '班级团队在农业图像检测领域取得重要进展...', image: 'https://picsum.photos/100/60?random=10' },
  { id: 2, title: '学院举办农业科技交流会', summary: '邀请专家学者共同探讨智慧农业发展趋势...', image: 'https://picsum.photos/100/60?random=11' },
  { id: 3, title: '学生科技创新大赛获奖', summary: '我班同学在省级科技创新比赛中荣获一等奖...', image: 'https://picsum.photos/100/60?random=12' }
])

const notices = ref([
  { id: 1, day: '17', date: '2026.04', title: '2026年度昆明学院智慧农业项目申报通知', summary: '请各班级按时提交项目申报材料...' },
  { id: 2, day: '15', date: '2026.04', title: '关于开展农业技术培训的通知', summary: '培训时间：4月20日至25日...' },
  { id: 3, day: '10', date: '2026.04', title: '智慧农业1班中期答辩安排', summary: '答辩时间：4月22日下午2点...' }
])

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

const prevSlide = () => {
  currentSlide.value = currentSlide.value === 0 ? slides.value.length - 1 : currentSlide.value - 1
}

const nextSlide = () => {
  currentSlide.value = currentSlide.value === slides.value.length - 1 ? 0 : currentSlide.value + 1
}
</script>
