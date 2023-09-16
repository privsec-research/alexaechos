script = document.createElement("script"); 
script.type = 'text/javascript'; 
script.id = "NotVeryUniqueID"; 
script.innerHTML = "Object.defineProperty(navigator, 'webdriver', {get: () => false}); document.getElementById('NotVeryUniqueID').remove();"; 
document.documentElement.prepend(script);