
from datetime import datetime

from airflow.models import DagRun
from airflow.utils.session import create_session


DAG_ID = "ecommerce_data_pipeline"


def monitor_pipeline():

    with create_session() as session:

        dag_run = (
            session.query(DagRun)
            .filter(DagRun.dag_id == DAG_ID)
            .order_by(DagRun.execution_date.desc())
            .first()
        )

        if dag_run is None:
            print("No DAG Run found.")
            return

        task_instances = dag_run.get_task_instances(session=session)

        print("=" * 65)
        print("E-COMMERCE DATA PIPELINE MONITORING")
        print("=" * 65)

        print("DAG ID :", dag_run.dag_id)
        print("Run ID :", dag_run.run_id)
        print("Status :", dag_run.state)

        if dag_run.start_date and dag_run.end_date:
            total_duration = (
                dag_run.end_date - dag_run.start_date
            ).total_seconds()

            print(f"Duration: {total_duration:.2f} seconds")

        print("-" * 65)

        states = {}

        for task in task_instances:
            state = task.state or "unknown"
            states[state] = states.get(state, 0) + 1

        total = len(task_instances)
        success = states.get("success", 0)
        failed = states.get("failed", 0)
        running = states.get("running", 0)

        print(f"Total Tasks : {total}")
        print(f"Success     : {success}")
        print(f"Failed      : {failed}")
        print(f"Running     : {running}")
        print("-" * 65)

        print(f"{'TASK':25} {'STATE':15} {'DURATION'}")
        print("-" * 65)

        for task in sorted(task_instances, key=lambda x: x.task_id):

            duration = "-"

            if task.start_date and task.end_date:
                seconds = (
                    task.end_date - task.start_date
                ).total_seconds()

                duration = f"{seconds:.2f}s"

            print(
                f"{task.task_id:25} "
                f"{str(task.state):15} "
                f"{duration}"
            )

        print("=" * 65)

        if total > 0 and success == total:
            print("PIPELINE RESULT: ALL TASKS SUCCESSFUL")
        elif failed > 0:
            print("PIPELINE RESULT: FAILED TASK DETECTED")
        else:
            print("PIPELINE RESULT: PIPELINE IN PROGRESS")


if __name__ == "__main__":
    monitor_pipeline()
