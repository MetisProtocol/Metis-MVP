/**
 *  此JS 属于通用信息提示框核心文件 , 使用本组件前 , 请确保已经加载自适应位置调整JS ， Jquery  以及CSS样式文件。
 */
var infoBox = {
    /**
     * 这个元素是提示框最外层的DIV元素 ， 我们称它为 ：主元素
     */
    thisElem : null,
    /**
     * 这个元素是上面那个元素的Jquert版本
     */
    thisJqueryElem : null,
    /**
     * 这个元素是提示框中的头部元素，它用于装放提示框头部显示的内容 ， 比如 ： 提示框主题。
     */
        thisElemHeadModule : null,
    /**
     * 这个元素是提示框中的正文元素，它用于装放提示框正文显示的内容 ， 比如 ： 提示框正文。
     */
        thisElemContentModule : null,
    /**
     * 这个元素是提示框中的选项元素，它用于装放提示框选项显示的内容 ， 比如 ： 好。
     */
        thisElemOptionModule : null,
    /**
     * 这个数组是 主元素 的Class数组列表。
     */
        thisElemClassList : null,
    /**
     * 这个设置是动画完成的时间，默认为400 ,必须和CSS中设置的动画时间同步，否则会无法判断正确的动画完成时间，导致某些功能的异常。
     */
        animationTime : 400,
    /**
     * 此变量判断信息框是否处于显示状态
     */
        isShow : false,
    /**
     * 此数组是任务队列 ， 假设你调用了信息框显示方法，但目前信息框的状态处于显示状态，则会将这个任务放入任务队列。（需要进行外部函数的设置来完善这个功能，本对象没有直接支持你这样操作，但它支持这样做。）
     */
        taskList : new Array(),
    /**
     * 任务队列中的任务个数
     */
        taskListCount : 0,

    /**
     *  添加一个显示任务到任务队列，当信息提示框处于显示状态，并希望在信息提示框关闭之后立即显示下一个任务，则可以调用这个方法添加一个任务，
     * @param data 数据。
     * @param beforeFun 前置函数 -- 需要在信息框弹出之前调用的函数。
     * @param afterFun  后置函数 -- 需要在信息框隐藏之后调用的函数。
     * @param beforeThat 前置函数this  -- 前置函数This 的指向。
     * @param afterThat  后置函数this  --后置函数This 的指向。
     * @param time  当信息提示框关闭之后，time 秒后调用下一个显示任务。
     */

        addTask : function(data,beforeFun,afterFun,beforeThat,afterThat,time){
            this.taskList[this.taskListCount] = {
                data:data,
                beforeFun:beforeFun,
                afterFun:afterFun,
                beforeThat:beforeThat,
                afterThat:afterThat,
                time:time
            }
            this.taskListCount++
        },
    /**
     * 从任务队列中删除一个任务。
     * @param info  这个任务的信息对象。
     */
        removeTask : function(info){
            for (let i = 0; i < this.taskListCount; i++) {
                if(this.taskList[i].data.info == info){
                    this.taskList.splice(i,1)
                    this.taskListCount--
                    return
                }
            }
        },
    /**
     * 执行任务队列中的任务。
     */

        executeTask : function(){
            if(this.taskListCount <= 0){
                return
            }
            let data = this.taskList[0]


            let that = this
            fun = function(that){
                that.loadInfoBox(data.data)
                that.showInfoBox(data.beforeFun,data.afterFun,data.beforeThat,data.afterThat)
                that.removeTask(data.data.info)
            }


            setTimeout(function(){
                fun(that)
            },data.time)
        },


    /**
     * 通过对象加载信息框。
      * @param data 对象。
     */

    loadInfoBox : function (data) {
            this.resetInfoBox()
            this.initClass(data)
            this.loadHeadModule(data)
            this.loadContentModule(data)
            this.loadOptionModule(data)
            autoPostionService.setDivAlign($(this.thisElem))
        },
    /**
     * 初始化方法。
     * @param id 目标DIV ， 调用此方法后，会将HTML 结构生成到你指定的DIV ，并初始化核心模块。
     */

        init : function(id){
            try {
                {
                    let infoBox = document.createElement("div")
                    infoBox.setAttribute("id", "infoBox")
                    infoBox.classList.add("align")
                    infoBox.style.display = "none"
                    let infoBox_body = document.createElement("div")
                    infoBox_body.classList.add("infoBox_body")

                    let infoBox_body_head = document.createElement("div")
                    infoBox_body_head.classList.add("infoBox_body_head")

                    let infoBox_body_content = document.createElement("div")
                    infoBox_body_content.classList.add("infoBox_body_content")

                    {
                        infoBox_body.appendChild(infoBox_body_head)
                        infoBox_body.appendChild(infoBox_body_content)
                    }

                    let infoBox_option = document.createElement("div")
                    infoBox_option.classList.add("infoBox_option")

                    {
                        infoBox.appendChild(infoBox_body)
                        infoBox.appendChild(infoBox_option)
                    }

                    document.querySelector("#" + id).appendChild(infoBox)

                }

                {
                    this.thisElem = document.querySelector("#infoBox")
                    this.thisJqueryElem = $(this.thisElem)
                    this.thisElemHeadModule = this.thisElem.querySelector(".infoBox_body_head")
                    this.thisElemContentModule = this.thisElem.querySelector(".infoBox_body_content")
                    this.thisElemOptionModule = this.thisElem.querySelector(".infoBox_option")
                    this.thisElemClassList = this.thisElem.classList
                }
            }catch (e) {
                throw new Error("Load infoHintModule Fail")
            }

        },


    /**
     * 重置信息提示框。
     * 清空里面的信息。
     */

    resetInfoBox : function(){
            this.thisElemHeadModule.innerHTML=""
            this.thisElemContentModule.innerHTML=""
            this.thisElemOptionModule.innerHTML=""
        },

        initClass : function (data) {
            let list = this.thisElemClassList
            for (let i = 0; i < list.length; i++) {
                if(list[i].length > 11 && list[i].substring(0,11) == "infoBox_img"){
                    list.remove(list[i])
                }
            }
            list.add(data.info.mainClass)
        },
    /**
     * 加载信息框头部信息。
     * @param data
     */
    loadHeadModule : function(data){
            let newElem = document.createElement("p")
            newElem.setAttribute("style","margin:0px")
            newElem.innerText = data.info.head
            this.thisElemHeadModule.appendChild(newElem)
        },
    /**
     * 加载信息框正文信息
     * @param data
     */
        loadContentModule : function (data) {
            let newElem = document.createElement("p")
            newElem.setAttribute("style","margin:0px")
            newElem.innerText = data.info.content
            this.thisElemContentModule.appendChild(newElem)
        },
    /**
     * 加载信息框选项信息
     * @param data
     */
        loadOptionModule : function (data) {

            for (let i = 0; i < data.info.option.length; i++) {
                let newElem = document.createElement("div")
                newElem.classList.add("infoBox_option_entity")
                newElem.setAttribute("i",i)
                newElem.innerText = data.info.option[i].span

                newElem.onclick =  function(){
                    data.info.option[this.getAttribute("i")].fun(data.data)
                }

                newElem.style.fontWeight = data.info.option[i].action?"200":"100"
                this.thisElemOptionModule.appendChild(newElem)

                /**
                 *  在所有选项元素之后插入分隔符,最后一个选项元素除外.
                 */
                {
                    if(i % 0 != 0 && i != data.info.option.length-1){
                        let newElemBr = document.createElement("div")
                        newElemBr.innerText="|"
                        newElemBr.classList.add("infoBox_option_br")
                        this.thisElemOptionModule.appendChild(newElemBr)
                    }
                }
            }
        },
    /**
     * 显示信息提示框。
     * @param beforeFun 前置函数 -- 在信息框显示之前调用这个函数，
     * @param afterFun  后置函数 -- 在信息框显示之后调用这个函数
     * @param beforeThat    前置函数This 指向
     * @param afterThat     后置函数This 指向
     */
        showInfoBox : function (beforeFun,afterFun,beforeThat,afterThat) {

            /**
             * 如果beforeFun函数不为空，则在执行 显示infoBox函数之前执行beforeFun函数
             */
            {
                if(beforeFun != null){
                    beforeFun.apply(beforeThat)
                }
            }

            /**
             * 显示InfoBox函数。
             */
            {
                this.thisElem.style.display = "inline-block"
                this.thisElem.classList.remove("infoBox_animation_hide")
                this.thisElem.classList.add("infoBox_animation_show")
                this.isShow = true
            }

            /**
             * 如果after函数不为空，则在执行 显示infoBox函数执行完之后执行afterFun函数
             */

            {
                if(afterFun!=null){
                    setTimeout( function() {
                        afterFun.apply(afterThat)
                    },this.animationTime)
                }
            }

        },
    /**
     * 隐藏信息框函数
     * @param beforeFun 前置函数 -- 隐藏信息框之前调用此函数
     * @param afterFun  后置函数 -- 隐藏信息框之后调用此函数
     * @param beforeThat    前置函数的This指向
     * @param afterThat     后置函数的This指向
     */
        hideInfoBox:function (beforeFun,afterFun,beforeThat,afterThat) {
            /**
             * 如果beforeFun函数不为空，则在执行 隐藏infoBox函数之前执行beforeFun函数
             */
            {
                if(beforeFun != null){
                    beforeFun.apply(beforeThat)
                }
            }
            /**
             * 隐藏InfoBox函数。
             */
            {
                this.thisElem.classList.remove("infoBox_animation_show")
                this.thisElem.classList.add("infoBox_animation_hide")

            }


            let that = this

            let fun = function(that){
                /**
                 *  隐藏infoBox函数执行完毕之后将盒子设置为隐藏
                 */
                that.thisElem.style.display = "none"
                /**
                 * 如果after函数不为空，则在执行 隐藏infoBox函数执行完毕之后执行afterFun函数
                 */
                {
                    that.isShow = false
                    if(afterFun != null){
                        afterFun.apply(afterThat)
                    }
                    that.executeTask()
                }
            }


            setTimeout(function () {
                fun(that)
            },this.animationTime)
        }
}










