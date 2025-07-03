import {defineAsyncComponent, h, render} from "vue";
import {  RouterView } from 'vue-router';

export default function RouterReplaceComp(component) {
  return {
    comp:component,
    name: 'routeReplaceSelf',
    computed: {
      // 获取当前页面组件，并将当前组件改为自己的组件
      currentPage() {
        // this.$route.matched[this.$route.matched.length - 1]获取当前匹配的子路由 路径 eg:testa/testb
        const curComp = this.$route.matched[this.$route.matched.length - 1]
        // 当前渲染页面
        const curPage = curComp.components.default.comp
        // 若当前子组件中没有渲染内容
        return curPage === component
      }
    },
    render() {
      // defineAsyncComponent 创建一个在需要时才会加载的异步组件
      // 若不同 则渲染 当前路由所对应的页面   若相同则渲染当前
      return this.currentPage?h(defineAsyncComponent(component)):h(RouterView)
    }
  }
}
