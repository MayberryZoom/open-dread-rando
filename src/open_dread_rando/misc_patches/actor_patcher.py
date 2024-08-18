import copy

from json_delta import patch

from open_dread_rando.patcher_editor import PatcherEditor


def _modify_actor(editor: PatcherEditor, original_reference: dict, modifications: list,
                  new_reference: dict, actor_groups: list, make_copy: bool = False):
    if new_reference:
        actor = copy.deepcopy(editor.resolve_actor_reference(original_reference))
        actor.sName = new_reference["actor"]
        scenario = editor.get_scenario(new_reference["scenario"])
    else:
        actor = editor.resolve_actor_reference(original_reference)
        scenario = editor.get_scenario(original_reference["scenario"])

    patch(actor, modifications)

    if new_reference:
        scenario.actors_for_layer(new_reference.get("layer", "default"))[new_reference["actor"]] = actor

    if actor_groups:
        reference = new_reference or original_reference
        for group in scenario.all_actor_groups():
            if (group in actor_groups):
                scenario.add_actor_to_group(group, reference["actor"], reference.get("layer", "default"))
            else:
                scenario.remove_actor_from_group(group, reference["actor"], reference.get("layer", "default"))

    if not make_copy and new_reference and new_reference is not original_reference:
        editor.remove_entity(original_reference, None)

def _remove_actor(editor: PatcherEditor, actor: dict):
    editor.remove_entity(actor["actor"], actor.get("map_category", None))

def apply_actor_patches(editor: PatcherEditor, actors_config: dict):
    if "modify" in actors_config:
        for actor in actors_config["modify"]:
            _modify_actor(
                editor,
                actor["actor"],
                actor["modifications"],
                actor.get("new_reference", None),
                actor.get("actor_groups", None),
                actor.get("copy", None)
            )

    if "remove" in actors_config:
        for actor in actors_config["remove"]:
            _remove_actor(editor, actor)
