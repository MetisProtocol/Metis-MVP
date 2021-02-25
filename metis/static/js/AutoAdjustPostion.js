var autoPostionService = {
     windowHeight : null,
     windowWidth : null,
     windowscrollHeight:null,
     windowscrollWidth:null,
     funList : new Array(),
     funListIndex : 0,

    /**
     * 节流函数
     * @param fn
     * @param delay
     * @returns {Function}
     */
    debounce : function(fn,delay,that){
        var timer = null;
        return function() {
            clearTimeout(timer);
            timer = setTimeout(function () {
                fn.apply(that);
            }, delay);
        };
    },


    /**
     * 此函数用来初始化整个核心模块 ， 若参数为 True 则代表将全局窗口改变大小事件托管给本对象，并立即执行 refresh() 函数 ， 反之则反。
     * @param bool
     */
    init : function(bool){
        try {
            this.getData()
            this.refresh()
            if (bool) {
                this.addEventFun(this.refresh)
                this.startMonitorWindowAlterSizeEvent()
            }
        }catch (e) {
            throw Error("Load AutoWindowUtil Fail")
        }
    },

    /**
     * 调用此函数意味着整个窗口改变大小的事件执行的事件都将指向 executeFunlist
     */
    startMonitorWindowAlterSizeEvent : function(){
         window.onresize = this.debounce(this.executeFunlist,300,this)
    },
    /**
     * 调用此函数意味着整个窗口改变大小的事件将指向空函数。
     */
    stopMonitorWindowAlterSizeEvent : function(){
         window.onresize = function () {}
    },

    /**
     * 此函数用于执行所有来自于函数列表中函数。
     */
    executeFunlist : function(){

        for (let i = 0; i < this.funListIndex; i++) {
            this.funList[i].apply(this)
        }
    },
    /**
     * 此函数用于添加一个函数对象到本对象的函数集合中。
     * @param fun
     */
    addEventFun : function(fun){
         this.funList[this.funListIndex] = fun
         this.funListIndex ++
    },
    /**
     * 此函数用于从本对象的函数集合中删除一个对象。
     * @param fun
     */
    removeEvent : function(fun){
        for (let i = 0; i < this.funListIndex; i++) {
            if(this.funList[i] == fun){
                this.funList.splice(i,1)
            }
        }
    },

    refresh : function(){
        this.getData()
        this.setDivRatio()
        this.setDivPostion()
    },

    /**
     * 此函数用来获取高宽比。
     */
    getData : function () {
         this.windowHeight = document.documentElement.clientHeight
         this.windowWidth = document.documentElement.clientWidth


     },

    /**
     * 此函数用来修改Div的高宽比.
     * 模式:auto
     * {
     *     高度和宽度全部取决于窗口的可用高宽比。
     * }
     * 模式:autoWidth
     * {
     *     宽度取决于窗口的可用宽度。
     * }
     */
    setDivRatio : function () {
            let autoList = document.querySelectorAll(".auto")
            {
                for (let i = 0; i < autoList.length; i++) {
                    let elem = $(autoList[i])
                    elem.css("height",this.windowHeight)
                    elem.css("width",this.windowWidth)
                }
            }
            let autoWidth = document.querySelectorAll(".autoWidth")
            {
                for (let i = 0; i < autoWidth.length; i++) {
                    let elem = $(autoWidth[i])
                    elem.css("width",this.windowWidth)
                }
            }
    },



    /**
     *  此函数用来修改Div的位置值
     *  模式：align
     *  {
     *      将所有Class包含align的Div 设置未居中并垂直对齐。
     *  }
     */
    setDivPostion : function () {

        let alignList = document.querySelectorAll(".align")
        {
            for (let i = 0; i < alignList.length; i++) {
                this.setDivAlign($(alignList[i]))
            }
        }
    },

    /**
     * 此函数用来将一个元素 居中。
     * @param elem
     */
    setDivAlign : function (elem) {
        let height = elem.css("height")
        let width = elem.css("width")
        let heightNumber =  parseInt(height.substring(0,height.indexOf("p")))
        let widthNumber = parseInt(width.substring(0,width.indexOf("p")))
        let y =  (this.windowHeight / 2) - (heightNumber / 2)
        let x =  (this.windowWidth / 2) - (widthNumber / 2)
        elem.css("top", y + "px" )
        elem.css("left", x + "px" )
    }

}



