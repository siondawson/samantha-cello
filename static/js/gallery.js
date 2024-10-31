var fullImgBox = document.getElementById("fullImgBox");
var fullImg = document.getElementById("fullImg");
document.getElementById('close').addEventListener('click', closeFullImg);

function openFullImg(pic) {
    fullImgBox.style.display = "flex";
    fullImg.src = pic;
}
function closeFullImg() {
    fullImgBox.style.display = "none";
}
