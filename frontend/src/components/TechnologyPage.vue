<template>
  <div class="min-h-screen bg-gray-50">
    <section class="bg-gradient-to-br from-blue-600 via-indigo-600 to-purple-600 text-white py-16">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center">
          <h1 class="text-4xl font-bold mb-4">技术开发</h1>
          <p class="text-lg text-blue-100">探索我们的技术栈和创新方案</p>
        </div>
      </div>
    </section>

    <section class="py-20 bg-white">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <h2 class="section-title text-center">核心技术</h2>
        <div class="grid md:grid-cols-2 gap-8">
          <div v-for="tech in technologies" :key="tech.title" class="card hover:-translate-y-1">
            <div class="flex items-start gap-4">
              <div class="w-12 h-12 bg-gradient-to-br from-primary-500 to-primary-700 rounded-xl flex items-center justify-center flex-shrink-0">
                <component :is="tech.icon" class="w-6 h-6 text-white" />
              </div>
              <div>
                <h3 class="text-xl font-semibold text-gray-800 mb-2">{{ tech.title }}</h3>
                <p class="text-gray-600 mb-4">{{ tech.description }}</p>
                <div class="flex flex-wrap gap-2">
                  <span v-for="tag in tech.tags" :key="tag" class="text-sm bg-primary-100 text-primary-700 px-3 py-1 rounded-full">
                    {{ tag }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="py-20 bg-gray-50">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <h2 class="section-title text-center">架构展示</h2>
        <div class="grid md:grid-cols-3 gap-6">
          <div v-for="architecture in architectures" :key="architecture.title" class="card">
            <div class="aspect-video bg-gray-100 rounded-xl overflow-hidden mb-4">
              <img :src="architecture.image" :alt="architecture.title" class="w-full h-full object-cover" />
            </div>
            <h3 class="text-lg font-semibold text-gray-800 mb-2">{{ architecture.title }}</h3>
            <p class="text-gray-600 text-sm">{{ architecture.description }}</p>
          </div>
        </div>
      </div>
    </section>

    <section class="py-20 bg-white">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <h2 class="section-title text-center">技术优势</h2>
        <div class="grid md:grid-cols-4 gap-6">
          <div v-for="advantage in advantages" :key="advantage.title" class="text-center">
            <div class="w-16 h-16 mx-auto mb-4 bg-gradient-to-br from-green-500 to-green-700 rounded-xl flex items-center justify-center">
              <component :is="advantage.icon" class="w-8 h-8 text-white" />
            </div>
            <h3 class="text-lg font-semibold text-gray-800 mb-2">{{ advantage.title }}</h3>
            <p class="text-gray-600 text-sm">{{ advantage.description }}</p>
          </div>
        </div>
      </div>
    </section>

    <section class="py-20 bg-gradient-to-br from-blue-50 to-purple-50">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <h2 class="section-title text-center">算法流程</h2>
        <div class="card">
          <div class="flex flex-col md:flex-row items-center justify-center gap-8 py-8">
            <div v-for="(step, index) in algorithmSteps" :key="index" class="flex flex-col items-center">
              <div class="w-16 h-16 bg-primary-600 rounded-full flex items-center justify-center text-white font-bold text-xl mb-3">
                {{ index + 1 }}
              </div>
              <h4 class="font-semibold text-gray-800 mb-1">{{ step.title }}</h4>
              <p class="text-gray-500 text-sm text-center">{{ step.description }}</p>
              <ArrowRight v-if="index < algorithmSteps.length - 1" class="w-6 h-6 text-gray-300 mt-4 hidden md:block" />
            </div>
          </div>
        </div>
      </div>
    </section>

    <footer class="bg-gray-800 text-white py-10">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center">
          <p class="text-gray-400">© 2024 智能图像检测平台. All rights reserved.</p>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Cpu, Database, Network, Shield, ArrowRight, Zap, Target, Clock, Lock } from 'lucide-vue-next'

const technologies = ref([
  { 
    title: '深度学习框架', 
    icon: Cpu,
    description: '基于PyTorch构建的高性能深度学习框架，支持多种神经网络模型训练和推理。',
    tags: ['PyTorch', 'TensorFlow', 'CUDA']
  },
  { 
    title: '图像预处理', 
    icon: Network,
    description: '先进的图像预处理算法，包括归一化、增强、裁剪等操作，提升模型训练效果。',
    tags: ['OpenCV', 'PIL', '数据增强']
  },
  { 
    title: '数据库架构', 
    icon: Database,
    description: '分布式数据库架构，支持海量数据存储和高效查询，确保系统稳定性。',
    tags: ['MySQL', 'Redis', 'MongoDB']
  },
  { 
    title: '安全防护', 
    icon: Shield,
    description: '多层次安全防护体系，包括数据加密、访问控制、异常检测等功能。',
    tags: ['SSL/TLS', 'JWT', '防火墙']
  }
])

const architectures = ref([
  { 
    title: '系统架构图', 
    image: 'https://picsum.photos/600/400?random=1', 
    description: '展示系统整体架构设计，包括前端、后端、数据库和AI服务层。' 
  },
  { 
    title: '数据流程图', 
    image: 'https://picsum.photos/600/400?random=2', 
    description: '数据从采集、处理到分析的完整流程可视化展示。' 
  },
  { 
    title: '模型架构', 
    image: 'https://picsum.photos/600/400?random=3', 
    description: '深度学习模型的网络结构和层次设计说明。' 
  }
])

const advantages = ref([
  { title: '高精度', icon: Target, description: '基于最新算法，检测准确率高达99.8%' },
  { title: '高性能', icon: Zap, description: '毫秒级响应，支持大规模并发处理' },
  { title: '高效率', icon: Clock, description: '智能优化算法，资源利用率最大化' },
  { title: '高安全', icon: Lock, description: '端到端加密，数据隐私严格保护' }
])

const algorithmSteps = ref([
  { title: '图像输入', description: '接收用户上传的图像数据' },
  { title: '预处理', description: '图像归一化和增强处理' },
  { title: '特征提取', description: '深度学习模型提取特征' },
  { title: '分类识别', description: '目标检测和分类处理' },
  { title: '结果输出', description: '返回检测结果和报告' }
])
</script>
