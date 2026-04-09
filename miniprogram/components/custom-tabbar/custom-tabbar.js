Component({
  properties: {
    current: {
      type: Number,
      value: 0
    },
    role: {
      type: String,
      value: 'student'
    }
  },

  data: {
    selected: 0,
    studentTabList: [
      {
        pagePath: '/pages/student/index/index',
        text: '首页'
      },
      {
        pagePath: '/pages/student/records/records',
        text: '记录'
      },
      {
        pagePath: '/pages/student/profile/profile',
        text: '我的'
      }
    ],
    teacherTabList: [
      {
        pagePath: '/pages/teacher/classes/classes',
        text: '班级'
      },
      {
        pagePath: '/pages/teacher/approvals/approvals',
        text: '审批'
      },
      {
        pagePath: '/pages/teacher/profile/profile',
        text: '我的'
      }
    ]
  },

  attached() {
    this.updateSelected();
  },

  observers: {
    'current': function(newVal) {
      this.setData({ selected: newVal });
    },
    'role': function(newVal) {
      this.updateSelected();
    }
  },

  methods: {
    updateSelected() {
      const currentPage = getCurrentPages();
      if (currentPage.length > 0) {
        const currentPath = currentPage[currentPage.length - 1].route;
        const tabList = this.data.role === 'teacher' ? this.data.teacherTabList : this.data.studentTabList;
        const index = tabList.findIndex(item => item.pagePath === `/${currentPath}`);
        if (index !== -1) {
          this.setData({ selected: index });
        }
      }
    },

    switchTab(e) {
      const index = e.currentTarget.dataset.index;
      const tabList = this.data.role === 'teacher' ? this.data.teacherTabList : this.data.studentTabList;
      const pagePath = tabList[index].pagePath;

      wx.reLaunch({ url: pagePath });
    }
  }
});