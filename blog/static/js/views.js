function respondToVisibility(element, callback) {
    var options = {
      root: document.documentElement,
    };
    var observer = new IntersectionObserver((entries, observer) => {
      entries.forEach(entry => {
        callback(entry.intersectionRatio > 0);
      });
    }, options);
    observer.observe(element);
  }