// ==================================================
// SMART FRIDGE SCRIPT
// ==================================================


// ==================================================
// GLOBAL
// ==================================================

let editingFoodId = null;

let stream = null;

let capturedImage = null;


// ==================================================
// HELPER
// ==================================================

function getElement(id) {

    return document.getElementById(id);

}


// ==================================================
// LOAD FOODS
// ==================================================

async function loadFoods() {

    const list = getElement("foodsList");

    list.innerHTML = `
        <div class="loading">
            กำลังโหลดข้อมูล...
        </div>
    `;

    try {

        const response = await fetch("/foods");

        const foods = await response.json();


        if (!Array.isArray(foods)) {

            list.innerHTML = `
                <div class="error-box">
                    ไม่สามารถโหลดข้อมูลอาหารได้
                </div>
            `;

            return;
        }


        if (foods.length === 0) {

            list.innerHTML = `
                <div class="empty-food">

                    <div class="empty-icon">
                        🥗
                    </div>

                    <p>
                        ยังไม่มีอาหารในตู้เย็น
                    </p>

                    <button
                        class="add-empty-btn"
                        onclick="openAddModal()"
                    >
                        ＋ เพิ่มอาหาร
                    </button>

                </div>
            `;

            return;
        }


        let html = "";


        foods.forEach(food => {

            const expiryInfo =
                getExpiryStatus(food.expiry);


            html += `

                <div class="food-card">

                    <div class="food-left">

                        <div class="food-icon">
                            ${getFoodIcon(food.name)}
                        </div>


                        <div class="food-info">

                            <h3>
                                ${escapeHtml(food.name)}
                            </h3>

                            <p>
                                ปริมาณ:
                                ${escapeHtml(food.quantity || "-")}
                            </p>

                            <p>
                                📍
                                ${escapeHtml(food.location || "-")}
                            </p>

                            <p class="${expiryInfo.className}">
                                📅 หมดอายุ:
                                ${escapeHtml(food.expiry)}
                                ${expiryInfo.text}
                            </p>

                        </div>

                    </div>


                    <div class="food-actions">

                        <button
                            class="edit-btn"
                            onclick="openEditModal(${food.id})"
                        >
                            ✏️ แก้ไข
                        </button>


                        <button
                            class="delete-btn"
                            onclick="removeFood(${food.id})"
                        >
                            🗑 ลบ
                        </button>

                    </div>

                </div>

            `;

        });


        list.innerHTML = html;

    } catch (error) {

        console.error(error);

        list.innerHTML = `
            <div class="error-box">
                เกิดข้อผิดพลาดในการโหลดข้อมูล
            </div>
        `;

    }

}


// ==================================================
// FOOD ICON
// ==================================================

function getFoodIcon(name) {

    const icons = {

        "หมู": "🥩",
        "ไก่": "🍗",
        "เนื้อวัว": "🥩",
        "ปลา": "🐟",
        "กุ้ง": "🦐",
        "ปลาหมึก": "🦑",
        "ปู": "🦀",
        "ไข่": "🥚",
        "นม": "🥛",
        "ชีส": "🧀",
        "ข้าว": "🍚",
        "ขนมปัง": "🍞",
        "แครอท": "🥕",
        "มันฝรั่ง": "🥔",
        "มะเขือเทศ": "🍅",
        "แตงกวา": "🥒",
        "เห็ด": "🍄",
        "แอปเปิล": "🍎",
        "กล้วย": "🍌",
        "ส้ม": "🍊",
        "แตงโม": "🍉",
        "สับปะรด": "🍍",
        "มะม่วง": "🥭",
        "อะโวคาโด": "🥑"

    };


    return icons[name] || "🥬";

}


// ==================================================
// ESCAPE HTML
// ==================================================

function escapeHtml(value) {

    if (value === null || value === undefined) {

        return "";

    }


    return String(value)

        .replace(/&/g, "&amp;")

        .replace(/</g, "&lt;")

        .replace(/>/g, "&gt;")

        .replace(/"/g, "&quot;")

        .replace(/'/g, "&#039;");

}


// ==================================================
// EXPIRY STATUS
// ==================================================

function getExpiryStatus(expiry) {

    if (!expiry) {

        return {
            className: "",
            text: ""
        };

    }


    const today =
        new Date();

    const expiryDate =
        new Date(expiry);


    today.setHours(0, 0, 0, 0);

    expiryDate.setHours(0, 0, 0, 0);


    const diff =
        Math.ceil(
            (
                expiryDate - today
            )
            /
            (
                1000 * 60 * 60 * 24
            )
        );


    if (diff < 0) {

        return {
            className: "expiry-danger",
            text: " • หมดอายุแล้ว"
        };

    }


    if (diff === 0) {

        return {
            className: "expiry-danger",
            text: " • หมดอายุวันนี้"
        };

    }


    if (diff <= 3) {

        return {
            className: "expiry-warning",
            text:
                ` • เหลือ ${diff} วัน`
        };

    }


    return {
        className: "expiry-normal",
        text:
            ` • เหลือ ${diff} วัน`
    };

}


// ==================================================
// ADD FOOD MODAL
// ==================================================

function openAddModal() {

    editingFoodId = null;


    getElement("modalTitle").innerText =
        "เพิ่มอาหาร";


    getElement("foodName").value =
        "";


    getElement("foodQuantity").value =
        "";


    getElement("foodLocation").value =
        "ช่องธรรมดา";


    getElement("foodExpiry").value =
        "";


    getElement("foodModal").style.display =
        "flex";

}


// ==================================================
// EDIT FOOD MODAL
// ==================================================

async function openEditModal(id) {

    try {

        const response =
            await fetch("/foods");


        const foods =
            await response.json();


        const food =
            foods.find(
                item => item.id === id
            );


        if (!food) {

            alert("ไม่พบข้อมูลอาหาร");

            return;

        }


        editingFoodId = id;


        getElement("modalTitle").innerText =
            "แก้ไขอาหาร";


        getElement("foodName").value =
            food.name || "";


        getElement("foodQuantity").value =
            food.quantity || "";


        getElement("foodLocation").value =
            food.location || "ช่องธรรมดา";


        getElement("foodExpiry").value =
            food.expiry || "";


        getElement("foodModal").style.display =
            "flex";


    } catch (error) {

        console.error(error);

        alert(
            "ไม่สามารถโหลดข้อมูลอาหารได้"
        );

    }

}


// ==================================================
// CLOSE ADD / EDIT MODAL
// ==================================================

function closeModal() {

    getElement("foodModal").style.display =
        "none";

}


// ==================================================
// SAVE FOOD
// ==================================================

async function saveFood() {

    const name =
        getElement("foodName")
            .value
            .trim();


    const quantity =
        getElement("foodQuantity")
            .value
            .trim()
            ||
            "ไม่ระบุ";


    const location =
        getElement("foodLocation")
            .value;


    const expiry =
        getElement("foodExpiry")
            .value;


    if (!name) {

        alert(
            "กรุณากรอกชื่อวัตถุดิบ"
        );

        return;

    }


    if (!expiry) {

        alert(
            "กรุณาเลือกวันหมดอายุ"
        );

        return;

    }


    const payload = {

        name:
            name,

        quantity:
            quantity,

        location:
            location,

        expiry:
            expiry

    };


    try {

        let response;


        // EDIT

        if (editingFoodId !== null) {

            response =
                await fetch(
                    `/foods/${editingFoodId}`,
                    {
                        method: "PUT",

                        headers: {
                            "Content-Type":
                                "application/json"
                        },

                        body:
                            JSON.stringify(
                                payload
                            )
                    }
                );

        }

        // ADD

        else {

            response =
                await fetch(
                    "/foods",
                    {
                        method: "POST",

                        headers: {
                            "Content-Type":
                                "application/json"
                        },

                        body:
                            JSON.stringify(
                                payload
                            )
                    }
                );

        }


        const data =
            await response.json();


        if (!data.success) {

            throw new Error(
                data.message ||
                "บันทึกข้อมูลไม่สำเร็จ"
            );

        }


        closeModal();


        editingFoodId = null;


        await loadFoods();


    } catch (error) {

        console.error(error);

        alert(
            "บันทึกข้อมูลไม่ได้\n" +
            error.message
        );

    }

}


// ==================================================
// DELETE FOOD
// ==================================================

async function removeFood(id) {

    const confirmDelete =
        confirm(
            "ต้องการลบอาหารรายการนี้หรือไม่?"
        );


    if (!confirmDelete) {

        return;

    }


    try {

        const response =
            await fetch(
                `/foods/${id}`,
                {
                    method: "DELETE"
                }
            );


        const data =
            await response.json();


        if (!data.success) {

            throw new Error(
                data.message ||
                "ลบข้อมูลไม่สำเร็จ"
            );

        }


        await loadFoods();


    } catch (error) {

        console.error(error);

        alert(
            "ลบข้อมูลไม่ได้\n" +
            error.message
        );

    }

}


// ==================================================
// CAMERA - OPEN
// ==================================================

async function openCameraModal() {

    const modal =
        getElement("cameraModal");


    const video =
        getElement("video");


    const preview =
        getElement("photoPreview");


    const useButton =
        getElement("usePhotoBtn");


    const result =
        getElement("scanResult");


    modal.style.display =
        "flex";


    capturedImage =
        null;


    preview.style.display =
        "none";


    preview.src =
        "";


    useButton.disabled =
        true;


    result.innerHTML =
        "";


    try {

        stream =
            await navigator.mediaDevices.getUserMedia(
                {
                    video: {
                        facingMode:
                            {
                                ideal:
                                    "environment"
                            }
                    },

                    audio: false
                }
            );


        video.srcObject =
            stream;


        await video.play();


    } catch (error) {

        console.error(error);


        result.innerHTML = `
            <div class="camera-error">
                ❌ ไม่สามารถเปิดกล้องได้
                <br>
                กรุณาอนุญาตการใช้กล้อง
            </div>
        `;

    }

}


// ==================================================
// CAMERA - CLOSE
// ==================================================

function closeCameraModal() {

    if (stream) {

        stream
            .getTracks()
            .forEach(
                track =>
                    track.stop()
            );


        stream =
            null;

    }


    const video =
        getElement("video");


    video.srcObject =
        null;


    getElement("cameraModal")
        .style.display =
        "none";

}


// ==================================================
// CAPTURE PHOTO
// ==================================================

function captureImage() {

    const video =
        getElement("video");


    if (!video.videoWidth) {

        getElement("scanResult")
            .innerHTML =
            "กล้องยังไม่พร้อม";

        return;

    }


    const canvas =
        document.createElement(
            "canvas"
        );


    canvas.width =
        video.videoWidth;


    canvas.height =
        video.videoHeight;


    const context =
        canvas.getContext(
            "2d"
        );


    context.drawImage(
        video,
        0,
        0,
        canvas.width,
        canvas.height
    );


    capturedImage =
        canvas.toDataURL(
            "image/jpeg",
            0.9
        );


    const preview =
        getElement(
            "photoPreview"
        );


    preview.src =
        capturedImage;


    preview.style.display =
        "block";


    // หยุดกล้อง

    if (stream) {

        stream
            .getTracks()
            .forEach(
                track =>
                    track.stop()
            );


        stream =
            null;

    }


    video.srcObject =
        null;


    getElement(
        "usePhotoBtn"
    ).disabled =
        false;


    getElement(
        "scanResult"
    ).innerHTML = `
        <span class="success-text">
            ✓ ถ่ายรูปเรียบร้อย
        </span>
    `;

}


// ==================================================
// USE PHOTO
// ==================================================

async function usePhoto() {

    if (!capturedImage) {

        return;

    }


    const result =
        getElement(
            "scanResult"
        );


    const button =
        getElement(
            "usePhotoBtn"
        );


    button.disabled =
        true;


    result.innerHTML = `
        <div class="ai-loading">

            <div class="spinner"></div>

            🤖 AI กำลังวิเคราะห์...

        </div>
    `;


    try {

        const response =
            await fetch(
                "/scan",
                {
                    method:
                        "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body:
                        JSON.stringify(
                            {
                                image:
                                    capturedImage
                            }
                        )
                }
            );


        const data =
            await response.json();


        if (!data.success) {

            throw new Error(
                data.message ||
                "AI วิเคราะห์ไม่สำเร็จ"
            );

        }


        const resultData =
            data.result;


        // ใส่ผล AI ลง Add Food

        getElement(
            "foodName"
        ).value =
            resultData.name || "";


        getElement(
            "foodQuantity"
        ).value =
            resultData.quantity ||
            "";


        getElement(
            "foodLocation"
        ).value =
            "ช่องธรรมดา";


        getElement(
            "foodExpiry"
        ).value =
            "";


        editingFoodId =
            null;


        getElement(
            "modalTitle"
        ).innerText =
            "เพิ่มอาหาร (ผลจาก AI)";


        // ปิด Scan

        closeCameraModal();


        // เปิด Add Food

        getElement(
            "foodModal"
        ).style.display =
            "flex";


    } catch (error) {

        console.error(error);


        result.innerHTML = `
            <div class="camera-error">

                ❌ AI วิเคราะห์ไม่สำเร็จ

                <br><br>

                ${escapeHtml(
                    error.message
                )}

            </div>
        `;


        button.disabled =
            false;

    }

}


// ==================================================
// AI MENU
// ==================================================

async function getMenuSuggestions() {

    const box =
        getElement(
            "menuResult"
        );


    box.innerHTML = `
        <div class="menu-loading">

            <div class="spinner"></div>

            🤖 AI กำลังวิเคราะห์
            วัตถุดิบในตู้เย็น...

        </div>
    `;


    try {

        const response =
            await fetch(
                "/menu-suggestions"
            );


        const data =
            await response.json();


        if (!data.success) {

            box.innerHTML = `
                <div class="error-box">

                    ❌
                    ${escapeHtml(
                        data.message ||
                        "AI ไม่สามารถวิเคราะห์ได้"
                    )}

                </div>
            `;

            return;

        }


        if (
            !data.menus ||
            data.menus.length === 0
        ) {

            box.innerHTML = `
                <div class="empty-menu">

                    ไม่พบเมนู

                </div>
            `;

            return;

        }


        let html = "";


        data.menus.forEach(
            (menu, index) => {


                const available =
                    menu
                        .available_ingredients
                        || [];


                const missing =
                    menu
                        .missing_ingredients
                        || [];


                const steps =
                    menu.steps
                        || [];


                html += `

                    <div class="menu-card">


                        <div class="menu-number">
                            ${index + 1}
                        </div>


                        <div class="menu-content">

                            <h3>
                                ${escapeHtml(
                                    menu.menu_name
                                )}
                            </h3>


                            <p class="menu-reason">

                                ${escapeHtml(
                                    menu.reason
                                )}

                            </p>


                            <div class="ingredient-group">

                                <strong>
                                    ✅ วัตถุดิบที่มี
                                </strong>

                                <p>
                                    ${
                                        available.length
                                        ?
                                        available
                                            .map(
                                                item =>
                                                    `<span class="ingredient-tag">${escapeHtml(item)}</span>`
                                            )
                                            .join("")
                                        :
                                        "ไม่มี"
                                    }
                                </p>

                            </div>


                            <div class="ingredient-group">

                                <strong>
                                    🛒 วัตถุดิบที่ขาด
                                </strong>

                                <p>

                                    ${
                                        missing.length
                                        ?
                                        missing
                                            .map(
                                                item =>
                                                    `<span class="missing-tag">${escapeHtml(item)}</span>`
                                            )
                                            .join("")
                                        :
                                        `<span class="complete-tag">ครบแล้ว ✅</span>`
                                    }

                                </p>

                            </div>


                            <div class="steps-group">

                                <strong>
                                    👨‍🍳 วิธีทำ
                                </strong>

                                <ol>

                                    ${
                                        steps
                                            .map(
                                                step =>
                                                    `<li>${escapeHtml(step)}</li>`
                                            )
                                            .join("")
                                    }

                                </ol>

                            </div>


                            ${
                                menu.use_expiring_soon
                                ?
                                `
                                    <div class="expiring-tip">

                                        ⚠️
                                        เมนูนี้ช่วยใช้
                                        วัตถุดิบที่ใกล้หมดอายุ

                                    </div>
                                `
                                :
                                ""
                            }

                        </div>

                    </div>

                `;

            }
        );


        box.innerHTML =
            html;


    } catch (error) {

        console.error(error);


        box.innerHTML = `
            <div class="error-box">

                ❌
                ไม่สามารถเชื่อมต่อ AI ได้

            </div>
        `;

    }

}


// ==================================================
// CLOSE MODALS WHEN CLICK OUTSIDE
// ==================================================

window.addEventListener(
    "click",
    function(event) {

        const foodModal =
            getElement(
                "foodModal"
            );


        const cameraModal =
            getElement(
                "cameraModal"
            );


        if (
            event.target ===
            foodModal
        ) {

            closeModal();

        }


        if (
            event.target ===
            cameraModal
        ) {

            closeCameraModal();

        }

    }
);


// ==================================================
// START
// ==================================================

window.addEventListener(
    "load",
    function() {

        loadFoods();

    }
);