const tags = document.querySelectorAll(".tag");
const hiddenInput = document.getElementById("help-needed-input");

if (tags.length > 0 && hiddenInput) {
  let selectedTags = [];

  tags.forEach((tag) => {
    tag.addEventListener("click", () => {
      // 1. UI par design badalne ke liye
      tag.classList.toggle("selected");
      
      const val = tag.getAttribute("data-value");
      
      // 2. Array mein check karo ki tag pehle se hai ya nahi
      if (selectedTags.includes(val)) {
        selectedTags = selectedTags.filter((t) => t !== val);
      } else {
        selectedTags.push(val);
      }
      
      // 3. Comma se separate karke hidden input mein value set karo taaki Django padh sake
      hiddenInput.value = selectedTags.join(",");
    });
  });
}
