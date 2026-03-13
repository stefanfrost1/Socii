"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { listProjects, listStages, updateProject } from "@/lib/api";
import { getToken } from "@/lib/supabase";
import { Project, ProjectStage } from "@/lib/types";
import Link from "next/link";
import {
  DndContext,
  DragEndEvent,
  PointerSensor,
  useSensor,
  useSensors,
  useDroppable,
} from "@dnd-kit/core";
import {
  SortableContext,
  useSortable,
  verticalListSortingStrategy,
} from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";

function ProjectCard({ project }: { project: Project }) {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({
    id: project.id,
    data: { project },
  });
  const style = { transform: CSS.Transform.toString(transform), transition, opacity: isDragging ? 0.5 : 1 };

  return (
    <div ref={setNodeRef} style={style} {...attributes} {...listeners} className="bg-white border rounded p-3 cursor-grab active:cursor-grabbing shadow-sm">
      <Link href={`/projects/${project.id}`} className="block" onClick={(e) => e.stopPropagation()}>
        <p className="text-sm font-medium">{project.name}</p>
        {project.value_estimate && (
          <p className="text-xs text-gray-500 mt-1">{project.currency} {Number(project.value_estimate).toLocaleString()}</p>
        )}
        {project.close_date_target && (
          <p className="text-xs text-gray-400">{project.close_date_target}</p>
        )}
      </Link>
    </div>
  );
}

function StageColumn({ stage, projects }: { stage: ProjectStage; projects: Project[] }) {
  const { setNodeRef } = useDroppable({ id: stage.id });
  return (
    <div className="bg-gray-100 rounded-lg p-3 w-64 shrink-0">
      <div className="flex items-center gap-2 mb-3">
        <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: stage.color }} />
        <h3 className="text-sm font-semibold">{stage.name}</h3>
        <span className="ml-auto text-xs text-gray-400">{projects.length}</span>
      </div>
      <div ref={setNodeRef} className="space-y-2 min-h-12">
        <SortableContext items={projects.map((p) => p.id)} strategy={verticalListSortingStrategy}>
          {projects.map((p) => <ProjectCard key={p.id} project={p} />)}
        </SortableContext>
      </div>
    </div>
  );
}

export default function KanbanPage() {
  const router = useRouter();
  const [token, setToken] = useState("");
  const [stages, setStages] = useState<ProjectStage[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);

  const sensors = useSensors(useSensor(PointerSensor, { activationConstraint: { distance: 5 } }));

  useEffect(() => {
    getToken().then((t) => {
      if (!t) { router.push("/login"); return; }
      setToken(t);
      Promise.all([listStages(t), listProjects({}, t)]).then(([s, p]: any[]) => {
        setStages(s);
        setProjects(p);
        setLoading(false);
      });
    });
  }, [router]);

  async function handleDragEnd(event: DragEndEvent) {
    const { active, over } = event;
    if (!over || active.id === over.id) return;

    const projectId = active.id as string;
    const targetStageId = over.id as string;

    // Check if dropping on a stage (column) vs another card
    const stage = stages.find((s) => s.id === targetStageId);
    if (!stage) return;

    setProjects((prev) =>
      prev.map((p) => (p.id === projectId ? { ...p, stage_id: targetStageId } : p))
    );
    await updateProject(projectId, { stage_id: targetStageId }, token).catch(() => {
      // Revert on error
      router.refresh();
    });
  }

  if (loading) return <div className="p-8 text-gray-500">Loading…</div>;

  const projectsByStage = stages.reduce((acc, stage) => {
    acc[stage.id] = projects.filter((p) => p.stage_id === stage.id);
    return acc;
  }, {} as Record<string, Project[]>);

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-xl font-semibold">Projects</h1>
        <div className="flex gap-2">
          <Link href="/projects/list" className="border px-3 py-1.5 rounded text-sm hover:bg-gray-50">List view</Link>
          <Link href="/projects/new" className="bg-blue-600 text-white px-4 py-1.5 rounded text-sm hover:bg-blue-700">+ New Project</Link>
        </div>
      </div>
      <DndContext sensors={sensors} onDragEnd={handleDragEnd}>
        <div className="flex gap-4 overflow-x-auto pb-4">
          {stages.map((stage) => (
            <StageColumn key={stage.id} stage={stage} projects={projectsByStage[stage.id] ?? []} />
          ))}
        </div>
      </DndContext>
    </div>
  );
}
