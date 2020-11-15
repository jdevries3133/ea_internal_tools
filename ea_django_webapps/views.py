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
                    <a href="/zoom-attendance">Click Here for a flashback to the internet of the 20th century.</a>
                    <p>... oh yeah, and to use the attendance thingy</p>
                </div>
            </body>
        </html>
        """,
        content_type='text/html'
    )

