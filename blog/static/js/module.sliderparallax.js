export default function(){CanvasAnimationFrame(),window.addEventListener("scroll",()=>{CanvasSliderParallax(),CanvasSliderElementsFade()},{passive:!0}),SEMICOLON.Core.getVars.resizers.sliderparallax=()=>SEMICOLON.Modules.sliderParallax()}const CanvasAnimationFrame=()=>{let s=0;var a=["ms","moz","webkit","o"];for(let e=0;e<a.length&&!window.requestAnimationFrame;++e)window.requestAnimationFrame=window[a[e]+"RequestAnimationFrame"],window.cancelAnimationFrame=window[a[e]+"CancelAnimationFrame"]||window[a[e]+"CancelRequestAnimationFrame"];window.requestAnimationFrame||(window.requestAnimationFrame=function(e,a){let l=(new Date).getTime(),r=Math.max(0,16-(l-s));var i=window.setTimeout(function(){e(l+r)},r);return s=l+r,i}),window.cancelAnimationFrame||(window.cancelAnimationFrame=function(e){clearTimeout(e)})},CanvasSliderParallax=()=>{var e=SEMICOLON.Core.getVars,a=e.sliderParallax;if("object"!=typeof a.el)return!0;let l=a.el,r=l.offsetHeight,i=l.classList,s,t;e.scrollPos.y=window.pageYOffset,e.elBody.classList.contains("device-up-lg")&&!SEMICOLON.Mobile.any()?(r+a.offset+50>e.scrollPos.y?(i.add("slider-parallax-visible"),i.remove("slider-parallax-invisible"),e.scrollPos.y>a.offset?("object"==typeof l.querySelector(".slider-inner")?(s=-.4*(e.scrollPos.y-a.offset),t=-.15*(e.scrollPos.y-a.offset),CanvasSliderParallaxSet(0,s,a.inner)):(s=(e.scrollPos.y-a.offset)/1.5,t=(e.scrollPos.y-a.offset)/7,CanvasSliderParallaxSet(0,s,l)),CanvasSliderParallaxSet(0,t,a.caption)):("object"==typeof l.querySelector(".slider-inner")?CanvasSliderParallaxSet(0,0,a.inner):CanvasSliderParallaxSet(0,0,l),CanvasSliderParallaxSet(0,0,a.caption))):(i.add("slider-parallax-invisible"),i.remove("slider-parallax-visible")),requestAnimationFrame(function(){CanvasSliderParallax(),CanvasSliderElementsFade()})):("object"==typeof l.querySelector(".slider-inner")?CanvasSliderParallaxSet(0,0,a.inner):CanvasSliderParallaxSet(0,0,l),CanvasSliderParallaxSet(0,0,a.caption),i.add("slider-parallax-visible"),i.remove("slider-parallax-invisible"))},CanvasSliderParallaxOffset=()=>{var e=SEMICOLON.Core,a=e.getVars.sliderParallax;let l=0;e.getVars.elHeader?.offsetHeight;e.getVars.elBody.classList.contains("side-header")||e.getVars.elHeader&&e.getNext(e.getVars.elHeader,".include-header").length,0<e.getNext(e.getVars.elSlider,"#header").length&&(l=0),a.offset=l},CanvasSliderParallaxSet=(e,a,l)=>{l&&(l.style.transform="translate3d("+e+", "+a+"px, 0)")},CanvasSliderElementsFade=()=>{let r=SEMICOLON.Core,e=r.getVars.sliderParallax;if(e.el.length<1)return!0;if(r.getVars.elBody.classList.contains("device-up-lg")&&!SEMICOLON.Mobile.any()){let a=e.el.offsetHeight,l;l=r.getVars.elHeader&&r.getVars.elHeader.classList.contains("transparent-header")||r.getVars.elBody.classList.contains("side-header")?100:0,e.el.classList.contains("slider-parallax-visible")&&e.el.querySelectorAll(".slider-arrow-left,.slider-arrow-right,.slider-caption,.slider-element-fade").forEach(e=>{e.style.opacity=1-1.85*(r.getVars.scrollPos.y-l)/a})}else e.el.querySelectorAll(".slider-arrow-left,.slider-arrow-right,.slider-caption,.slider-element-fade").forEach(e=>e.style.opacity=1)};