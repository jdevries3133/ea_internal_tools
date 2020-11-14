from django.http import HttpResponse

def home(request):
    """
    Luxurious home page
    """
    return HttpResponse(
        """
        <html>
            <head></head>
            <body>
                <div>
                    <h1>Zoom Attendance Reporter</h1>
                    <a href="/zoom-attendance">Click Here</a>
                </div>
            </body>
        </html>
        """,
        content_type='text/html'
    )

