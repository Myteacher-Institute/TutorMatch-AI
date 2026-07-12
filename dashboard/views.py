from accounts.models import UserProfile
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.apps import apps
from accounts.decorators import admin_required
from tutors.models import Tutor
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum, Count, Q
import json


def home(request):
    featured_tutors = [
        {
            "id": 1,
            "name": "Dr. Samuel Adebayo",
            "title": "MSc. Applied Mathematics",
            "rate": "5k",
            "rating": "4.9",
            "tags": ["Mathematics", "Physics", "JAMB/WAEC"],
            "photo": "https://images.unsplash.com/photo-1560250097-0b93528c311a?auto=format&fit=crop&w=700&q=80",
        },
        {
            "id": 2,
            "name": "Sarah Johnson",
            "title": "IELTS/TOEFL Expert",
            "rate": "4.5k",
            "rating": "5.0",
            "tags": ["English", "Literature", "Diction"],
            "photo": "https://images.unsplash.com/photo-1580894732444-8ecded7900cd?auto=format&fit=crop&w=700&q=80",
        },
        {
            "id": 3,
            "name": "Chidi Okoro",
            "title": "Senior Software Engineer",
            "rate": "8k",
            "rating": "4.8",
            "tags": ["Python", "Web Dev", "Scratch"],
            "photo": "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?auto=format&fit=crop&w=700&q=80",
        },
    ]
    return render(request, "home.html", {"featured_tutors": featured_tutors})


def about(request):
    return render(request, "about.html")


def contact(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")
        return render(request, "contact.html", {"success": True, "name": name})
    return render(request, "contact.html")


@admin_required
def admin_dashboard(request):
    total_tutors = UserProfile.objects.filter(role=UserProfile.ROLE_TUTOR).count()
    total_students = UserProfile.objects.filter(role=UserProfile.ROLE_STUDENT).count()

    total_bookings = 0
    total_revenue = "0.00"
    total_commission = "0.00"
    total_tutor_payout = "0.00"

    Booking = None
    Payment = None
    try:
        Booking = apps.get_model("bookings", "Booking")
        total_bookings = Booking.objects.count()
    except (LookupError, AttributeError):
        pass

    try:
        Payment = apps.get_model("payments", "Payment")
        from django.db.models import Sum
        received_amount = Payment.objects.filter(
            payment_status__in=["paid", "released"]
        ).aggregate(Sum("amount"))["amount__sum"] or 0
        total_revenue = f"{float(received_amount):,.2f}"
        total_commission = f"{float(received_amount) * 0.15:,.2f}"
        total_tutor_payout = f"{float(received_amount) * 0.85:,.2f}"
    except (LookupError, AttributeError, ValueError):
        pass

    today = timezone.now().date()
    last_7_days = [today - timedelta(days=i) for i in range(6, -1, -1)]
    day_labels = [d.strftime("%a") for d in last_7_days]

    user_growth = []
    booking_growth = []
    revenue_growth = []

    for d in last_7_days:
        day_start = timezone.make_aware(timezone.datetime.combine(d, timezone.datetime.min.time()))
        day_end = day_start + timedelta(days=1)
        user_growth.append(UserProfile.objects.filter(created_at__gte=day_start, created_at__lt=day_end).count())
        if Booking:
            booking_growth.append(Booking.objects.filter(created_at__gte=day_start, created_at__lt=day_end).count())
        else:
            booking_growth.append(0)
        if Payment:
            day_revenue = Payment.objects.filter(created_at__gte=day_start, created_at__lt=day_end, payment_status__in=["paid", "released"]).aggregate(Sum("amount"))["amount__sum"] or 0
            revenue_growth.append(float(day_revenue))
        else:
            revenue_growth.append(0.0)

    booking_status_counts = {
        "completed": 0,
        "accepted": 0,
        "pending": 0,
        "cancelled": 0,
    }
    if Booking:
        qs = Booking.objects.values("status").annotate(c=Count("id"))
        for row in qs:
            booking_status_counts[row["status"]] = row["c"]

    top_tutors = []
    if Payment:
        try:
            payout_rows = (
                Payment.objects
                .filter(payment_status__in=["paid", "released"])
                .values("booking__tutor")
                .annotate(total_payout=Sum("tutor_payout"), sessions=Count("id"))
                .order_by("-total_payout")[:2]
            )
            tutor_ids = [r["booking__tutor"] for r in payout_rows if r["booking__tutor"]]
            tutor_map = {
                t.id: t
                for t in Tutor.objects.filter(id__in=tutor_ids).select_related("user__user")
            }
            for r in payout_rows:
                t = tutor_map.get(r["booking__tutor"])
                if not t:
                    continue
                top_tutors.append({
                    "name": t.get_full_name or t.username,
                    "photo": t.profile_photo,
                    "payout": float(r["total_payout"]),
                    "sessions": r["sessions"],
                })
        except (LookupError, AttributeError, TypeError):
            pass

    recent_activities = []

    for profile in UserProfile.objects.select_related("user").order_by("-created_at")[:10]:
        recent_activities.append({
            "timestamp": profile.created_at,
            "text": f"New account registered: {profile.user.get_full_name() or profile.user.username} ({profile.get_role_display()})",
            "icon": "fa-user-plus",
            "color": "#2563eb",
            "bg": "#eff6ff",
        })

    if Booking:
        for b in Booking.objects.select_related("student__user", "tutor__user").order_by("-created_at")[:10]:
            recent_activities.append({
                "timestamp": b.created_at,
                "text": f"Booking {b.status} — {b.student.user.get_full_name() or b.student.user.username} with {b.tutor.user.user.get_full_name() or b.tutor.user.user.username}",
                "icon": "fa-calendar-check",
                "color": "#16a34a" if b.status == "completed" else "#f59e0b" if b.status == "accepted" else "#ef4444" if b.status == "cancelled" else "#64748b",
                "bg": "#dcfce7" if b.status == "completed" else "#fef3c7" if b.status == "accepted" else "#fef2f2" if b.status == "cancelled" else "#f1f5f9",
            })

    if Payment:
        for p in Payment.objects.select_related("booking__student__user").order_by("-created_at")[:10]:
            recent_activities.append({
                "timestamp": p.created_at,
                "text": f"Payment {p.payment_status} — ₦{float(p.amount):,.2f} from {p.booking.student.user.get_full_name() or p.booking.student.user.username}",
                "icon": "fa-money-bill-wave",
                "color": "#16a34a" if p.payment_status == "paid" else "#ef4444" if p.payment_status == "failed" else "#f59e0b",
                "bg": "#dcfce7" if p.payment_status == "paid" else "#fef2f2" if p.payment_status == "failed" else "#fef3c7",
            })

    ChatSession = None
    try:
        ChatSession = apps.get_model("Chat", "ChatSession")
    except (LookupError, AttributeError):
        pass
    if ChatSession:
        for c in ChatSession.objects.select_related("student", "tutor").order_by("-created_at")[:10]:
            recent_activities.append({
                "timestamp": c.created_at,
                "text": f"Chat started between {c.student.username} and {c.tutor.username}",
                "icon": "fa-comments",
                "color": "#8b5cf6",
                "bg": "#f3e8ff",
            })

    recent_activities.sort(key=lambda x: x["timestamp"], reverse=True)
    recent_activities = recent_activities[:20]

    metrics = {
        "total_tutors": total_tutors,
        "total_students": total_students,
        "total_bookings": total_bookings,
        "total_revenue": total_revenue,
        "total_commission": total_commission,
        "total_tutor_payout": total_tutor_payout,
    }

    context = {
        "metrics": metrics,
        "today": today,
        "chart_labels": json.dumps(day_labels),
        "user_growth": json.dumps(user_growth),
        "booking_growth": json.dumps(booking_growth),
        "revenue_growth": json.dumps(revenue_growth),
        "booking_status_counts": booking_status_counts,
        "recent_activities": recent_activities,
        "top_tutors": top_tutors,
    }
    return render(request, "dashboard/admin_dashboard.html", context)


@admin_required
def export_weekly_report(request):
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import mm
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable,
    )
    from django.db.models import Sum, Count, Q
    from django.http import HttpResponse

    today = timezone.now().date()
    week_start = today - timedelta(days=6)
    last_7_days = [today - timedelta(days=i) for i in range(6, -1, -1)]

    Booking = Payment = None
    try:
        Booking = apps.get_model("bookings", "Booking")
    except (LookupError, AttributeError):
        pass
    try:
        Payment = apps.get_model("payments", "Payment")
    except (LookupError, AttributeError):
        pass

    total_tutors = UserProfile.objects.filter(role=UserProfile.ROLE_TUTOR).count()
    total_students = UserProfile.objects.filter(role=UserProfile.ROLE_STUDENT).count()
    total_bookings = Booking.objects.count() if Booking else 0

    total_collected = 0.0
    total_commission = 0.0
    total_payout = 0.0
    received_amount = 0.0
    if Payment:
        received = Payment.objects.filter(payment_status__in=["paid", "released"])
        received_amount = float(received.aggregate(Sum("amount"))["amount__sum"] or 0)
        total_collected = received_amount
        total_commission = total_collected * 0.15
        total_payout = float(received.filter(payment_status="released").aggregate(Sum("tutor_payout"))["tutor_payout__sum"] or 0)

    day_revenue = []
    for d in last_7_days:
        day_start = timezone.make_aware(timezone.datetime.combine(d, timezone.datetime.min.time()))
        day_end = day_start + timedelta(days=1)
        if Payment:
            rev = float(Payment.objects.filter(created_at__gte=day_start, created_at__lt=day_end, payment_status__in=["paid", "released"]).aggregate(Sum("amount"))["amount__sum"] or 0)
        else:
            rev = 0.0
        day_revenue.append((d.strftime("%a, %b %d"), rev))

    booking_status_counts = {"completed": 0, "accepted": 0, "pending": 0, "cancelled": 0}
    if Booking:
        for row in Booking.objects.values("status").annotate(c=Count("id")):
            booking_status_counts[row["status"]] = row["c"]

    top_tutors = []
    if Payment:
        try:
            payout_rows = (
                Payment.objects
                .filter(payment_status__in=["paid", "released"])
                .values("booking__tutor")
                .annotate(total_payout=Sum("tutor_payout"), sessions=Count("id"))
                .order_by("-total_payout")[:5]
            )
            tutor_ids = [r["booking__tutor"] for r in payout_rows if r["booking__tutor"]]
            tutor_map = {
                t.id: t
                for t in Tutor.objects.filter(id__in=tutor_ids).select_related("user__user")
            }
            for r in payout_rows:
                t = tutor_map.get(r["booking__tutor"])
                if not t:
                    continue
                top_tutors.append((t.get_full_name or t.username, int(r["sessions"]), float(r["total_payout"])))
        except (LookupError, AttributeError, TypeError):
            pass

    naira = lambda v: "₦{:,.2f}".format(v)

    styles = getSampleStyleSheet()
    brand = colors.HexColor("#2563eb")
    dark = colors.HexColor("#0f172a")
    muted = colors.HexColor("#64748b")
    line = colors.HexColor("#e2e8f0")

    title_style = ParagraphStyle("TitleX", parent=styles["Title"], textColor=dark, fontSize=22, spaceAfter=2)
    sub_style = ParagraphStyle("Sub", parent=styles["Normal"], textColor=muted, fontSize=10, alignment=TA_CENTER)
    h_style = ParagraphStyle("H", parent=styles["Heading2"], textColor=brand, fontSize=13, spaceBefore=14, spaceAfter=6)
    cell_style = ParagraphStyle("Cell", parent=styles["Normal"], fontSize=9.5, textColor=dark)
    cell_muted = ParagraphStyle("CellM", parent=styles["Normal"], fontSize=9.5, textColor=muted)
    label_style = ParagraphStyle("Label", parent=styles["Normal"], fontSize=9, textColor=muted, alignment=TA_CENTER)
    value_style = ParagraphStyle("Value", parent=styles["Normal"], fontSize=15, textColor=dark, alignment=TA_CENTER, leading=18)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="weekly_report_{}.pdf"'.format(today.strftime("%Y-%m-%d"))

    doc = SimpleDocTemplate(
        response, pagesize=A4,
        leftMargin=18 * mm, rightMargin=18 * mm, topMargin=18 * mm, bottomMargin=18 * mm,
        title="Myteacherconnect Weekly Report",
    )
    elems = []

    elems.append(Paragraph("Myteacherconnect", title_style))
    elems.append(Paragraph("Weekly Platform Report &nbsp;|&nbsp; {} – {}".format(
        week_start.strftime("%b %d, %Y"), today.strftime("%b %d, %Y")), sub_style))
    elems.append(Spacer(1, 6))
    elems.append(HRFlowable(width="100%", thickness=1.2, color=brand))
    elems.append(Spacer(1, 12))

    metrics = [
        ("Total Tutors", str(total_tutors)),
        ("Total Students", str(total_students)),
        ("Total Bookings", str(total_bookings)),
        ("Revenue Collected", naira(total_collected)),
        ("Platform Commission", naira(total_commission)),
        ("Tutor Payouts", naira(total_payout)),
    ]
    metric_cells = []
    for label, value in metrics:
        inner = [Paragraph(label, label_style), Paragraph(value, value_style)]
        metric_cells.append(inner)
    metric_rows = [metric_cells[i:i + 3] for i in range(0, len(metric_cells), 3)]
    metric_table = Table(metric_rows, colWidths=[58 * mm] * 3)
    metric_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ("BOX", (0, 0), (-1, -1), 0.5, line),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, line),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
    ]))
    elems.append(metric_table)

    elems.append(Paragraph("Revenue — Last 7 Days", h_style))
    rev_data = [[Paragraph("Day", cell_style), Paragraph("Revenue", cell_style)]]
    for day, rev in day_revenue:
        rev_data.append([Paragraph(day, cell_style), Paragraph(naira(rev), cell_style)])
    rev_data.append([Paragraph("Total", cell_style), Paragraph(naira(sum(r for _, r in day_revenue)), cell_style)])
    rev_table = Table(rev_data, colWidths=[120 * mm, 54 * mm])
    rev_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), brand),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, line),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#eff6ff")),
    ]))
    elems.append(rev_table)

    elems.append(Paragraph("Booking Status", h_style))
    status_data = [[Paragraph("Status", cell_style), Paragraph("Count", cell_style)]]
    for status in ["completed", "accepted", "pending", "cancelled"]:
        status_data.append([Paragraph(status.title(), cell_style), Paragraph(str(booking_status_counts.get(status, 0)), cell_style)])
    status_table = Table(status_data, colWidths=[120 * mm, 54 * mm])
    status_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), brand),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, line),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    elems.append(status_table)

    elems.append(Paragraph("Top Tutors by Payout", h_style))
    if top_tutors:
        tutor_data = [[Paragraph("Tutor", cell_style), Paragraph("Sessions", cell_style), Paragraph("Payout", cell_style)]]
        for name, sessions, payout in top_tutors:
            tutor_data.append([Paragraph(name, cell_style), Paragraph(str(sessions), cell_style), Paragraph(naira(payout), cell_style)])
        tutor_table = Table(tutor_data, colWidths=[108 * mm, 33 * mm, 33 * mm])
        tutor_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), brand),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.5, line),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        elems.append(tutor_table)
    else:
        elems.append(Paragraph("No payouts recorded yet.", cell_muted))

    elems.append(Spacer(1, 16))
    elems.append(HRFlowable(width="100%", thickness=0.6, color=line))
    elems.append(Paragraph(
        "Generated on {} by Myteacherconnect Admin Console.".format(timezone.now().strftime("%Y-%m-%d %H:%M")),
        cell_muted))

    doc.build(elems)
    return response


@admin_required
def verifications(request):
    action = request.POST.get("action")
    profile_id = request.POST.get("profile_id")
    if request.method == "POST" and action and profile_id:
        try:
            profile = UserProfile.objects.get(pk=profile_id)
            if action == "approve":
                profile.is_verified = True
                profile.save()

                try:
                    tutor_obj = Tutor.objects.filter(user=profile).first()
                    if tutor_obj:
                        tutor_obj.verification_status = "approved"
                        tutor_obj.save(update_fields=["verification_status"])
                        tutor_obj.documents.update(verification_status="approved")
                except (LookupError, AttributeError):
                    pass

            elif action == "reject":
                profile.is_verified = False
                profile.save()

                try:
                    tutor_obj = Tutor.objects.filter(user=profile).first()
                    if tutor_obj:
                        tutor_obj.verification_status = "rejected"
                        tutor_obj.save(update_fields=["verification_status"])
                        tutor_obj.documents.update(verification_status="rejected")
                except (LookupError, AttributeError):
                    pass
        except UserProfile.DoesNotExist:
            pass

    pending_tutors = Tutor.objects.filter(
        verification_status__in=["pending", "rejected"]
    ).select_related("user__user").prefetch_related("documents").order_by("-user__created_at")
    return render(request, "dashboard/verifications.html", {"pending_tutors": pending_tutors})


@admin_required
def users(request):
    action = request.POST.get("action")
    user_id = request.POST.get("user_id")
    if request.method == "POST" and action and user_id:
        try:
            profile = UserProfile.objects.get(pk=user_id)
            if action == "toggle_verify":
                profile.is_verified = not profile.is_verified
                profile.save()
                if not profile.is_verified:
                    Tutor = apps.get_model("tutors", "Tutor")
                    tutor_obj = Tutor.objects.filter(user=profile).first()
                    if tutor_obj:
                        tutor_obj.verification_status = "rejected"
                        tutor_obj.save(update_fields=["verification_status"])
                        tutor_obj.documents.update(verification_status="rejected")
            elif action == "delete":
                profile.user.delete()
        except UserProfile.DoesNotExist:
            pass

    query = request.GET.get("q", "").strip()
    user_qs = UserProfile.objects.all().order_by("-created_at")
    if query:
        user_qs = user_qs.filter(
            user__username__icontains=query
        ) | user_qs.filter(
            user__email__icontains=query
        ) | user_qs.filter(
            user__first_name__icontains=query
        ) | user_qs.filter(
            user__last_name__icontains=query
        ) | user_qs.filter(
            phone_number__icontains=query
        )

    paginator = Paginator(user_qs, 15)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "dashboard/users.html",
        {
            "user_list": page_obj.object_list,
            "page_obj": page_obj,
            "paginator": paginator,
            "query": query,
        },
    )


@admin_required
def bookings(request):
    Booking = None
    try:
        Booking = apps.get_model("bookings", "Booking")
    except (LookupError, AttributeError):
        pass

    booking_list = []
    status_counts = {
        "pending": 0,
        "accepted": 0,
        "completed": 0,
        "cancelled": 0,
    }
    total_value = 0.0

    if Booking:
        try:
            base_qs = Booking.objects.select_related(
                "student__user", "tutor__user__user"
            ).order_by("-created_at")

            # Summary metrics are computed over ALL bookings, not just the current page
            status_rows = Booking.objects.values("status").annotate(c=Count("id"))
            for row in status_rows:
                status_counts[row["status"]] = row["c"]
            total_value = float(
                base_qs.exclude(status="cancelled").aggregate(Sum("amount"))["amount__sum"] or 0
            )

            status_filter = request.GET.get("status", "").strip()
            qs = base_qs
            if status_filter in status_counts:
                qs = qs.filter(status=status_filter)

            paginator = Paginator(qs, 10)
            page_number = request.GET.get("page")
            page_obj = paginator.get_page(page_number)

            for b in page_obj.object_list:
                booking_list.append({
                    "id": b.id,
                    "student": b.student.user.get_full_name if b.student and b.student.user else (b.student.user.username if b.student and b.student.user else "-"),
                    "student_email": b.student.user.email if b.student and b.student.user else "",
                    "tutor": b.tutor.get_full_name if b.tutor else (b.tutor.username if b.tutor else "-"),
                    "tutor_photo": b.tutor.profile_photo if b.tutor else "",
                    "booking_date": b.booking_date,
                    "lesson_time": b.lesson_time,
                    "amount": float(b.amount),
                    "status": b.status,
                    "note": b.lesson_note,
                    "created_at": b.created_at,
                })
        except (LookupError, AttributeError, TypeError):
            pass

    context = {
        "booking_list": booking_list,
        "status_counts": status_counts,
        "total_value": total_value,
        "active_filter": request.GET.get("status", ""),
        "paginator": paginator,
        "page_obj": page_obj,
    }
    return render(request, "dashboard/bookings.html", context)


@admin_required
def revenue(request):
    Payment = None
    try:
        Payment = apps.get_model("payments", "Payment")
    except (LookupError, AttributeError):
        pass

    if request.method == "POST":
        action = request.POST.get("action")
        payment_id = request.POST.get("payment_id")
        if Payment and payment_id:
            try:
                payment = Payment.objects.get(pk=payment_id)
                if action == "mark_paid":
                    payment.payment_status = "paid"
                elif action == "release":
                    payment.payment_status = "released"
                payment.save(update_fields=["payment_status"])
            except Payment.DoesNotExist:
                pass
        return redirect("admin_revenue")

    summary = {
        "total_collected": 0.0,
        "total_commission": 0.0,
        "total_payout": 0.0,
        "pending_amount": 0.0,
        "failed_amount": 0.0,
        "paid_sessions": 0,
        "pending_sessions": 0,
        "failed_sessions": 0,
    }
    tutor_payouts = []
    recent_payments = []

    if Payment:
        try:
            received = Payment.objects.filter(payment_status__in=["paid", "released"])
            released = Payment.objects.filter(payment_status="released")
            pending = Payment.objects.filter(payment_status__in=["pending", "paid"])
            failed = Payment.objects.filter(payment_status="failed")

            summary["total_collected"] = float(received.aggregate(Sum("amount"))["amount__sum"] or 0)
            summary["total_commission"] = float(received.aggregate(Sum("commission"))["commission__sum"] or 0)
            summary["total_payout"] = float(released.aggregate(Sum("tutor_payout"))["tutor_payout__sum"] or 0)
            summary["pending_amount"] = float(pending.aggregate(Sum("tutor_payout"))["tutor_payout__sum"] or 0)
            summary["failed_amount"] = float(failed.aggregate(Sum("amount"))["amount__sum"] or 0)
            summary["paid_sessions"] = received.count()
            summary["pending_sessions"] = pending.count()
            summary["failed_sessions"] = failed.count()

            payout_rows = (
                Payment.objects
                .values("booking__tutor")
                .annotate(
                    total_collected=Sum("amount", filter=Q(payment_status__in=["paid", "released"])),
                    total_commission=Sum("commission", filter=Q(payment_status__in=["paid", "released"])),
                    total_payout=Sum("tutor_payout", filter=Q(payment_status="released")),
                    paid_sessions=Count("id", filter=Q(payment_status__in=["paid", "released"])),
                    pending_sessions=Count("id", filter=Q(payment_status="pending")),
                    sessions=Count("id"),
                )
                .order_by("-total_collected")
            )
            tutor_ids = [r["booking__tutor"] for r in payout_rows if r["booking__tutor"]]
            tutor_map = {
                t.id: t
                for t in Tutor.objects.filter(id__in=tutor_ids).select_related("user__user")
            }
            for r in payout_rows:
                t = tutor_map.get(r["booking__tutor"])
                if not t:
                    continue
                has_pending = (r["pending_sessions"] or 0) > 0
                tutor_payouts.append({
                    "name": t.get_full_name or t.username,
                    "photo": t.profile_photo,
                    "email": t.user.user.email if t.user and t.user.user else "",
                    "total_collected": float(r["total_collected"] or 0),
                    "total_commission": float(r["total_commission"] or 0),
                    "total_payout": float(r["total_payout"] or 0),
                    "paid_sessions": r["paid_sessions"] or 0,
                    "pending_sessions": r["pending_sessions"] or 0,
                    "sessions": r["sessions"] or 0,
                    "status": "Pending Payout" if has_pending else "Paid",
                })

            for p in Payment.objects.select_related("booking__tutor__user__user", "booking__student__user").order_by("-created_at"):
                tutor = p.booking.tutor if p.booking else None
                student = p.booking.student if p.booking else None
                booking_status = p.booking.status if p.booking else "pending"
                booking_status_label = p.booking.get_status_display() if p.booking else "Pending"
                if booking_status == "cancelled":
                    booking_status_label = "Rejected"
                recent_payments.append({
                    "id": p.id,
                    "reference": p.paystack_reference or "-",
                    "tutor": tutor.get_full_name if tutor else "-",
                    "student": student.user.get_full_name if student and student.user else (student.user.username if student and student.user else "-"),
                    "amount": float(p.amount),
                    "commission": float(p.commission),
                    "payout": float(p.tutor_payout),
                    "status": p.payment_status,
                    "booking_status": booking_status,
                    "booking_status_label": booking_status_label,
                    "created_at": p.created_at,
                    "account_name": tutor.account_name if tutor else "",
                    "bank_name": tutor.bank_name if tutor else "",
                    "account_number": tutor.account_number if tutor else "",
                })

            ledger_paginator = Paginator(recent_payments, 10)
            ledger_page = ledger_paginator.get_page(request.GET.get("page"))

            today = timezone.now().date()
            last_7_days = [today - timedelta(days=i) for i in range(6, -1, -1)]
            chart_labels = [d.strftime("%a") for d in last_7_days]
            revenue_growth = []
            payout_growth = []
            for d in last_7_days:
                day_start = timezone.make_aware(timezone.datetime.combine(d, timezone.datetime.min.time()))
                day_end = day_start + timedelta(days=1)
                day_rev = received.filter(created_at__gte=day_start, created_at__lt=day_end).aggregate(Sum("amount"))["amount__sum"] or 0
                day_payout = released.filter(created_at__gte=day_start, created_at__lt=day_end).aggregate(Sum("tutor_payout"))["tutor_payout__sum"] or 0
                revenue_growth.append(float(day_rev))
                payout_growth.append(float(day_payout))
        except (LookupError, AttributeError, TypeError):
            pass

    context = {
        "summary": summary,
        "tutor_payouts": tutor_payouts,
        "recent_payments": recent_payments,
        "ledger_paginator": ledger_paginator,
        "ledger_page": ledger_page,
        "chart_labels": json.dumps(chart_labels),
        "revenue_growth": json.dumps(revenue_growth),
        "payout_growth": json.dumps(payout_growth),
    }
    return render(request, "dashboard/revenue.html", context)


def Termsofservice(request):
    return render(request, "Terms_of_Service.html")


def privacy_policy(request):
    return render(request, "privacy_policy.html")