// pages/student/class-records.js
import api from '../../network/api.js';
import utils from '../../utils/utils.js';

Page({
  data: {
    todayDate: '',
    classRecords: [],
    totalCount: 0,
    punchedCount: 0,
    leaveCount: 0,
    unpunchedCount: 0
  },

  onLoad() {
    this.setTodayDate();
    this.loadClassRecords();
  },

  setTodayDate() {
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const day = String(now.getDate()).padStart(2, '0');
    const weekDays = ['日', '一', '二', '三', '四', '五', '六'];
    const weekDay = weekDays[now.getDay()];
    
    this.setData({
      todayDate: `${year}年${month}月${day}日 星期${weekDay}`
    });
  },

  async loadClassRecords() {
    try {
      const userInfo = utils.getUserInfo();
      if (!userInfo || !userInfo.class) {
        utils.showToast('无法获取班级信息', 'none');
        return;
      }

      const className = userInfo.class;
      const res = await api.student.getClassRecords(className);

      if (res.success) {
        const records = res.data || [];
        
        let punchedCount = 0;
        let leaveCount = 0;
        let unpunchedCount = 0;

        records.forEach(record => {
          if (record.on_leave) {
            leaveCount++;
          } else if (record.punched) {
            punchedCount++;
          } else {
            unpunchedCount++;
          }
        });

        this.setData({
          classRecords: records,
          totalCount: records.length,
          punchedCount,
          leaveCount,
          unpunchedCount
        });
      } else {
        utils.showToast(res.message || '加载失败', 'none');
      }
    } catch (err) {
      console.error('加载班级记录失败:', err);
      utils.showToast('网络错误，请重试', 'none');
    }
  },

  onRefresh() {
    this.loadClassRecords();
  }
});
