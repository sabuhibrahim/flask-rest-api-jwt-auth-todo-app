from flask import request
from pydantic import ValidationError
from pydantic.error_wrappers import ErrorWrapper
from sqlalchemy.orm import joinedload
from todo_app import app, db
from todo_app.decorators import auth_required
from todo_app.models import TaskList, Task, Step, User
from todo_app.exceptions import NotFoundException, BadRequestException
from todo_app.hash import get_password_hash, verify_password
from todo_app.jwt import create_token_pair
from todo_app.schemas import (
    TaskListScheme,
    TaskScheme,
    TaskListCreateScheme,
    TaskCreateScheme,
    TaskPartialUpdateSchema,
    UpdateOrderScheme,
    StepCreateScheme,
    StepScheme,
    UserRegister,
    UserLogin,
    User as UserSchema,
)


GET = "GET"
POST = "POST"
PUT = "PUT"
PATCH = "PATCH"
DELETE = "DELETE"


# ----------------- Login, Register views -------------------
@app.route("/login", methods=[POST])
def login():
    data = UserLogin(**request.json)
    user = User.query.filter_by(email=data.email).first()

    if not user or not verify_password(data.password, user.password):
        raise BadRequestException("Incorrect email or password")

    token_pair = create_token_pair(user=UserSchema.from_orm(user))

    return {"access": token_pair.access.token, "refresh": token_pair.refresh.token}, 200


@app.route("/register", methods=[POST])
def register():
    data = UserRegister(**request.json)
    user = User.query.filter_by(email=data.email).first()
    if user:
        raise BadRequestException("Email has already registered")

    # hashing password
    user_data = data.dict(exclude={"confirm_password"})
    user_data["password"] = get_password_hash(user_data["password"])

    # save user to db
    user = User(**user_data)
    user.is_active = True

    db.session.add(user)
    db.session.commit()

    return {"msg": "Successfully registered"}


# ----------------- TaskList list, create, update order view -------------
@app.route("/tasklist", methods=[GET, POST, PATCH])
@auth_required
def tasklists_view(user):
    if request.method == POST:
        tasklist_data = TaskListCreateScheme(**request.json)
        tasklist = TaskList(**tasklist_data.dict())
        tasklist.user_id = user.id

        tasklist.order = 1
        last_task = (
            TaskList.query.filter_by(user_id=user.id)
            .order_by(TaskList.order.desc(), TaskList.created_at.desc())
            .first()
        )
        if last_task:
            tasklist.order += last_task.order

        db.session.add(tasklist)
        db.session.commit()

        return TaskListScheme.from_orm(tasklist).dict(), 201

    elif request.method == PATCH:
        order_data = UpdateOrderScheme(**request.json)

        query = TaskList.query.filter_by(user_id=user.id)

        tasklists = query.order_by(TaskList.order.desc(), TaskList.created_at.desc())
        tasklist = query.filter_by(id=order_data.id).first()

        if not tasklist:
            raise ValidationError(
                errors=[ErrorWrapper(ValueError("Tasklist is not found"), loc="id")]
            )

        last_order = tasklists.first()
        if last_order.order < order_data.order:
            raise ValidationError(
                errors=[
                    ErrorWrapper(
                        ValueError("Value is bigger than tasklists count"), loc="order"
                    )
                ]
            )
        updated_tasklists = []
        for tl in tasklists:
            if tl.id == tasklist.id:
                continue
            c = False
            if order_data.order <= tl.order and tasklist.order > tl.order:
                c = True
                tl.order += 1
            elif order_data.order >= tl.order and tasklist.order < tl.order:
                c = True
                tl.order -= 1
            if c:
                updated_tasklists.append(tl)

        tasklist.order = order_data.order
        updated_tasklists.append(tasklist)
        db.session.bulk_save_objects(updated_tasklists)
        db.session.commit()

    tasklists = TaskList.query.filter_by(user_id=user.id).order_by(
        TaskList.order.asc(), TaskList.created_at.asc()
    )

    return [TaskListScheme.from_orm(tasklist).dict() for tasklist in tasklists], 200


# -------- Tasklist Detail and update view --------
@app.route("/tasklist/<uuid:tasklist_id>", methods=[GET, PUT, DELETE])
@auth_required
def tasklist_view(user, tasklist_id):
    tasklist: TaskList = TaskList.query.filter_by(
        user_id=user.id, id=tasklist_id
    ).first()
    if not tasklist:
        raise NotFoundException(message="Tasklist Not Found")

    if request.method == PUT:
        return _tasklist_view_put(tasklist)
    elif request.method == DELETE:
        db.session.delete(tasklist)
        db.session.commit()
        return None, 200

    return TaskListScheme.from_orm(tasklist).dict(), 200


def _tasklist_view_put(tasklist: TaskList):
    """Update tasklist"""
    tasklist_data = TaskListCreateScheme(**request.json())

    tasklist.title = tasklist_data.title
    tasklist.description = tasklist_data.description
    db.session.commit()

    return TaskListScheme.from_orm(tasklist).dict(), 200


# Tasks list, create, update order view
@app.route("/tasklist/<uuid:tasklist_id>/tasks", methods=[GET, POST, PATCH])
@auth_required
def tasks_view(user, tasklist_id):
    tasklist: TaskList = TaskList.query.filter_by(
        user_id=user.id, id=tasklist_id
    ).first()
    if not tasklist:
        raise NotFoundException(message="Tasklist Not Found")

    if request.method == POST:
        return _tasks_view_post(tasklist)

    elif request.method == PATCH:
        return _tasks_view_patch(tasklist)

    is_completed = request.args.get("is_completed", "false") == "true"
    return [
        TaskScheme.from_orm(task).dict()
        for task in Task.query.options(joinedload(Task.steps)).filter_by(
            tasklist_id=tasklist_id, is_completed=is_completed
        )
    ], 200


def _tasks_view_post(tasklist: TaskList):
    """Create new task"""
    task_data = TaskCreateScheme(**request.json)
    task_data_dict = task_data.dict()

    steps_data = task_data_dict.pop("steps")

    task = Task(**task_data_dict)
    task.tasklist_id = tasklist.id
    task.order = 1

    last_task = (
        Task.query.filter_by(tasklist_id=tasklist.id, is_completed=False)
        .order_by(Task.order.desc(), Task.created_at.desc())
        .first()
    )

    if last_task:
        task.order += last_task.order

    db.session.add(task)
    db.session.commit()
    if steps_data:
        steps = [Step(**data) for data in steps_data]
        for step in steps:
            step.task_id = task.id

        db.session.add_all(steps)
        db.session.commit()

    return TaskScheme.from_orm(task).dict(), 201


def _tasks_view_patch(tasklist: TaskList):
    """Update task order"""
    task_data = UpdateOrderScheme(**request.json())
    task: Task = Task.query.filter_by(tasklist_id=tasklist.id, id=task_data.id).first()
    if not task:
        raise ValidationError(
            errors=[ErrorWrapper(ValueError("Task is not found"), loc="id")]
        )

    tasks = (
        Task.query.filter(Task.id != task_data.id)
        .filter_by(tasklist_id=tasklist.id)
        .order_by(Task.order.desc(), Task.created_at.desc())
    )
    last_task: Task = tasks.first()

    if last_task.order < task_data.order:
        raise ValidationError(
            errors=[
                ErrorWrapper(
                    ValueError("Value is bigger than tasks count"), loc="order"
                )
            ]
        )

    updated_tasks = []
    for t in tasks:
        c = False
        if task_data.order <= t.order and task.order > t.order:
            c = True
            t.order += 1
        elif task_data.order >= t.order and task.order < t.order:
            c = True
            t.order -= 1
        if c:
            updated_tasks.append(t)

    task.order = task_data.order
    updated_tasks.append(task)
    db.session.bulk_save_objects(updated_tasks)
    db.session.commit()

    return [
        TaskScheme.from_orm(task).dict()
        for task in Task.query.options(joinedload(Task.steps))
        .filter_by(tasklist_id=tasklist.id)
        .order_by()
    ], 200


@app.route(
    "/tasklist/<uuid:tasklist_id>/tasks/<uuid:task_id>",
    methods=[GET, PATCH, DELETE],
)
@auth_required
def task_view(user, tasklist_id, task_id):
    tasklist: TaskList = TaskList.query.filter_by(
        user_id=user.id, id=tasklist_id
    ).first()

    if not tasklist:
        raise NotFoundException("Tasklist not found")

    task: Task = (
        Task.query.options(joinedload(Task.steps))
        .filter_by(tasklist_id=tasklist.id, id=task_id)
        .first()
    )

    if not task:
        raise NotFoundException("Task not found")

    if request.method == PATCH:
        task_data = TaskPartialUpdateSchema(**request.json).dict(exclude_unset=True)
        for key in Task.__table__.columns.keys():
            if key in task_data:
                setattr(task, key, task_data[key])
        db.session.commit()

    elif request.method == DELETE:
        db.session.delete(task)
        db.session.commit()
        return None, 200

    return TaskScheme.from_orm(task).dict(), 200


@app.route("/tasklist/<uuid:tasklist_id>/tasks/<uuid:task_id>/steps", methods=[POST])
def steps_view(user, tasklist_id, task_id):
    tasklist: TaskList = TaskList.query.filter_by(
        user_id=user.id, id=tasklist_id
    ).first()

    if not tasklist:
        raise NotFoundException("Tasklist not found")

    task: Task = Task.query.filter_by(tasklist_id=tasklist.id, id=task_id).first()

    if not task:
        raise NotFoundException("Task not found")

    step_data = StepCreateScheme(**request.json)
    step = Step(**step_data)
    step.task_id = task.id
    db.session.add(step)
    db.session.commit()
    return StepScheme.from_orm(step).dict(), 201


@app.route(
    "/tasklist/<uuid:tasklist_id>/tasks/<uuid:task_id>/steps/<uuid:step_id>",
    methods=[PUT, DELETE],
)
def step_view(user, tasklist_id, task_id, step_id):
    tasklist: TaskList = TaskList.query.filter_by(
        user_id=user.id, id=tasklist_id
    ).first()

    if not tasklist:
        raise NotFoundException("Tasklist not found")

    task: Task = Task.query.filter_by(tasklist_id=tasklist.id, id=task_id).first()

    if not task:
        raise NotFoundException("Task not found")

    step = Step.query.filter_by(id=step_id, task_id=task_id).first()

    if request.method == DELETE:
        db.session.delete(step)
        db.session.commit()
        return None, 200

    step_data = StepCreateScheme(**request.json)
    step.title = step_data.title
    db.session.commit()

    return StepScheme.from_orm(step).dict(), 200
