import { defineStore } from "pinia";
import { ref, computed } from "vue";
import { api } from "@/api";

interface TrainingParams {
  page?: number;
  page_size?: number;
  search?: string;
  status?: string;
}

export const useTrainingStore = defineStore("training", () => {
  const trainingJobs = ref<any[]>([]);
  const currentJob = ref<any>(null);
  const loading = ref(false);
  const pagination = ref({
    page: 1,
    page_size: 20,
    total: 0,
    pages: 0
  });

  const activeJobs = computed(() => 
    trainingJobs.value.filter(job => job.status === "running")
  );
  
  const completedJobs = computed(() => 
    trainingJobs.value.filter(job => job.status === "completed")
  );
  
  const failedJobs = computed(() => 
    trainingJobs.value.filter(job => job.status === "failed")
  );

  const getTrainingJobs = async (params: TrainingParams = {}) => {
    try {
      loading.value = true;
      const response = await api.training.list();
      if (response.data.success) {
        trainingJobs.value = response.data.data.items;
        pagination.value = {
          page: response.data.data.page,
          page_size: response.data.data.page_size,
          total: response.data.data.total,
          pages: response.data.data.pages
        };
      } else {
        console.error("获取训练任务列表失败:", response.data.message);
      }
    } catch (error) {
      console.error("获取训练任务列表失败:", error);
    } finally {
      loading.value = false;
    }
  };

  const getTrainingJob = async (id: string) => {
    try {
      loading.value = true;
      const response = await api.training.get(id);
      if (response.data.success) {
        currentJob.value = response.data.data;
        return response.data.data;
      } else {
        console.error("获取训练任务详情失败:", response.data.message);
        return null;
      }
    } catch (error) {
      console.error("获取训练任务详情失败:", error);
      return null;
    } finally {
      loading.value = false;
    }
  };

  const createTrainingJob = async (jobData: any) => {
    try {
      loading.value = true;
      const response = await api.training.create(jobData);
      if (response.data.success) {
        console.log("训练任务创建成功");
        await getTrainingJobs();
        return response.data.data;
      } else {
        console.error("创建训练任务失败:", response.data.message);
        return null;
      }
    } catch (error) {
      console.error("创建训练任务失败:", error);
      return null;
    } finally {
      loading.value = false;
    }
  };

  const updateTrainingJob = async (id: string, jobData: any) => {
    try {
      loading.value = true;
      const response = await api.training.update(id, jobData);
      if (response.data.success) {
        console.log("训练任务更新成功");
        await getTrainingJobs();
        return response.data.data;
      } else {
        console.error("更新训练任务失败:", response.data.message);
        return null;
      }
    } catch (error) {
      console.error("更新训练任务失败:", error);
      return null;
    } finally {
      loading.value = false;
    }
  };

  const deleteTrainingJob = async (id: string) => {
    try {
      loading.value = true;
      const response = await api.training.delete(id);
      if (response.data.success) {
        console.log("训练任务删除成功");
        await getTrainingJobs();
        return true;
      } else {
        console.error("删除训练任务失败:", response.data.message);
        return false;
      }
    } catch (error) {
      console.error("删除训练任务失败:", error);
      return false;
    } finally {
      loading.value = false;
    }
  };

  const startTrainingJob = async (id: string) => {
    try {
      loading.value = true;
      const response = await api.training.start(id);
      if (response.data.success) {
        console.log("训练任务启动成功");
        await getTrainingJobs();
        return true;
      } else {
        console.error("启动训练任务失败:", response.data.message);
        return false;
      }
    } catch (error) {
      console.error("启动训练任务失败:", error);
      return false;
    } finally {
      loading.value = false;
    }
  };

  const stopTrainingJob = async (id: string) => {
    try {
      loading.value = true;
      const response = await api.training.stop(id);
      if (response.data.success) {
        console.log("训练任务停止成功");
        await getTrainingJobs();
        return true;
      } else {
        console.error("停止训练任务失败:", response.data.message);
        return false;
      }
    } catch (error) {
      console.error("停止训练任务失败:", error);
      return false;
    } finally {
      loading.value = false;
    }
  };

  const getTrainingLogs = async (jobId: string, params = {}) => {
    try {
      loading.value = true;
      // 这里需要根据实际API调整
      const response = await api.training.get(jobId);
      if (response.data.success) {
        return response.data.data.logs || [];
      } else {
        console.error("获取训练日志失败:", response.data.message);
        return null;
      }
    } catch (error) {
      console.error("获取训练日志失败:", error);
      return null;
    } finally {
      loading.value = false;
    }
  };

  const reset = () => {
    trainingJobs.value = [];
    currentJob.value = null;
    loading.value = false;
    pagination.value = {
      page: 1,
      page_size: 20,
      total: 0,
      pages: 0
    };
  };

  return {
    trainingJobs,
    currentJob,
    loading,
    pagination,
    activeJobs,
    completedJobs,
    failedJobs,
    getTrainingJobs,
    getTrainingJob,
    createTrainingJob,
    updateTrainingJob,
    deleteTrainingJob,
    startTrainingJob,
    stopTrainingJob,
    getTrainingLogs,
    reset
  };
});