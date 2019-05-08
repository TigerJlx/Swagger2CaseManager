import Vue from 'vue'
import Router from 'vue-router'
import store from '../store'
import Login from '../components/auth/Login'
import Register from '../components/auth/Register'
import Home from '../components/home/Home'
import ProjectList from '../components/main_view/project/project'
import ProjectDetail from '../components/main_view/project/ProjectDetail'
import APIView from '../components/main_view/test_api/APIView'
import AutoTest from '../components/main_view/test_case/AutoTest'
import ReportList from '../components/main_view/report/report'

Vue.use(Router);  // Vue 导入vue-router插件

const router = new Router({
  mode: 'history',
  routes: [
    {
      path: '/waykichain/register/',
      name: 'Register',
      component: Register,
      meta: {
        title: '用户注册'
      }
    },
    {
      path: '/waykichain/login/',
      name: 'Login',
      component: Login,
      meta: {
        title: '用户登录'
      }
    },
    {
      path: '/waykichain',
      name: 'Index',
      component: Home,
      meta: {
        title: '首页',
        requireAuth: true
      },
      children: [
        {
          name: 'ProjectList',
          path: 'project_list',
          component: ProjectList,
          meta: {
            title: '项目列表',
            requireAuth: true,
          }
        },
        {
          name: 'ProjectDetail',
          path: 'project/:id/dashbord', // router中的id就是this.$router.id,注意语法格式（带:）
          component: ProjectDetail,
          meta: {
            title: '项目预览',
            requireAuth: true,
          }
        },
        // {
        //   name: 'DebugTalk',
        //   path: 'debugtalk/:id',
        //   component: DebugTalk,
        //   meta: {
        //     title: '编辑驱动',
        //     requireAuth: true,
        //   }
        //
        // },
        {
          name: 'APIView',
          path: 'api_record/:id',
          component: APIView,
          meta: {
            title: '接口模板',
            requireAuth: true
          }

        },
        {
          name: 'AutoTest',
          path: 'auto_test/:id',
          component: AutoTest,
          meta: {
            title: '自动化测试',
            requireAuth: true
          }

        },
        // {
        //   name: 'RecordConfig',
        //   path: 'record_config/:id',
        //   component: RecordConfig,
        //   meta: {
        //     title: '配置管理',
        //     requireAuth: true
        //   }
        //
        // },
        // {
        //   name: 'GlobalEnv',
        //   path: 'global_env/:id',
        //   component: GlobalEnv,
        //   meta: {
        //     title: '全局变量',
        //     requireAuth: true
        //   }
        //
        // },
        {
          name: 'Reports',
          path: 'reports/:id',
          component: ReportList,
          meta: {
            title: '历史报告',
            requireAuth: true
          }

        },
        // {
        //   name: 'Task',
        //   path: 'tasks/:id',
        //   component: Tasks,
        //   meta: {
        //     title: '定时任务',
        //     requireAuth: true
        //   }
        //
        // },
        // {
        //   name: 'HostIP',
        //   path: 'host_ip/:id',
        //   component: HostAddress,
        //   meta: {
        //     title: 'HOST配置',
        //     requireAuth: true
        //   }
        //
        // }
      ]
    }

  ]
});

// 给路由先注册一个beforEach钩子函数
// 在路由跳转时，会自动调用这个钩子函数
// from ==》to表示从上一个路由跳转到下一个路由
router.beforeEach((to, from, next) => {
    // console.log("to", to)
    // console.log("from", from)
    // console.log("next", next)
    /* 路由发生变化修改页面title */
    setTimeout((res) => {
        if (to.meta.title) {
            document.title = to.meta.title;
            var routerNameObject = {
              "项目列表": 'ProjectList',
              "项目预览": 'ProjectDetail',
              "接口模板": 'APIView',
              "自动化测试": 'AutoTest',
              "历史报告": 'Reports',
            };
            store.state.routerName = routerNameObject[to.meta.title];
            // this.setLocalValue("routerName",routerNameObject[to.meta.title]);
        }

        if (to.meta.requireAuth) {
            if (store.state.token !== "null") {
                next();
            } else {
                next({
                    name: 'Login',
                })
            }
        }
        else {
            next()
        }
    })

});

export default router
