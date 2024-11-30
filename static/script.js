document.getElementById('generateQR').addEventListener('click', function() {
    const subject = document.getElementById('subject').value;
    const section = document.getElementById('section').value;

    // Ensure subject and section are filled
    if (subject && section) {
        const qrCodeData = `Subject: ${subject}, Section: ${section}`;
        
        // Generate QR code using a library like QRCode.js
        const qrCodeElement = document.getElementById('qrCode');
        const qr = new QRCode(qrCodeElement, {
            text: qrCodeData,
            width: 128,
            height: 128,
        });

        // Show the QR Code container and enable the stop button
        document.getElementById('qrContainer').style.display = 'block';
        document.getElementById('stopAttendance').disabled = false;
    } else {
        alert("Please enter subject and section.");
    }
});

document.addEventListener('DOMContentLoaded', function () {
    const stopButton = document.getElementById('stopAttendance');
    if (stopButton) {
        stopButton.addEventListener('click', function () {
            // Enable the download options after "Stop" is clicked
            const downloadOptions = document.getElementById('downloadOptions');
            if (downloadOptions) {
                downloadOptions.style.display = 'block';
            }
        });
    }
});


document.addEventListener('DOMContentLoaded', function () {
    const downloadExcelBtn = document.getElementById('downloadExcel');
    if (downloadExcelBtn) {
        downloadExcelBtn.addEventListener('click', function () {
            const data = [
                { Name: 'Mohamed', StudentId: '12345', Time: '12:00 PM' },
                { Name: 'Ahmed', StudentId: '67890', Time: '12:05 PM' },
            ]; // Replace with actual attendance data

            const ws = XLSX.utils.json_to_sheet(data);
            const wb = XLSX.utils.book_new();
            XLSX.utils.book_append_sheet(wb, ws, 'Attendance');
            XLSX.writeFile(wb, 'attendance_report.xlsx');
        });
    }
});

document.addEventListener('DOMContentLoaded', function () {
    const downloadPDFBtn = document.getElementById('downloadPDF');
    if (downloadPDFBtn) {
        downloadPDFBtn.addEventListener('click', function () {
            const doc = new jsPDF();
            doc.autoTable({
                head: [['Name', 'Student ID', 'Time']],
                body: [
                    ['Mohamed', '12345', '12:00 PM'],
                    ['Ahmed', '67890', '12:05 PM'],
                ], // Replace with actual attendance data
            });
            doc.save('attendance_report.pdf');
        });
    }
});

function refreshQR() {
    console.log("Refreshing QR...");
    fetch('/refresh_qr')
        .then(response => response.json())
        .then(data => {
            console.log("Data received:", data);
            if (data.qr_image) {
                let qrImage = document.getElementById('qrCodeImage');
                if (!qrImage) {
                    const qrContainer = document.getElementById('qrContainer');
                    if (qrContainer) {
                        qrImage = document.createElement('img');
                        qrImage.id = 'qrCodeImage';
                        qrImage.alt = 'QR Code';
                        qrContainer.appendChild(qrImage);
                    }
                }
                if (qrImage) {
                    qrImage.src = data.qr_image + '?t=' + new Date().getTime(); // منع التخزين المؤقت
                }
            }
        })
        .catch(error => console.error('Error refreshing QR:', error));
}

// تحديث QR كل 5 ثوانٍ
setInterval(refreshQR, 5000);


