# @staticmethod
#     def lvdt_map(lvdt_adc: int) -> float:
#         return lvdt_adc / 0b0000_1111_1111_1111 * 10

# # spoilers: RET
# sensors_state.levers_state.spoilers_lever = V_TRIState.DOWN
# plane_commands = create_plane_commands(fjs_state, sensors_state)
# assert plane_commands.spoiler_right_deg == 0
# assert plane_commands.spoiler_left_deg == 0

# # spoilers: RET - flaps: FULL
# fjs_state.fjs_axes_state.flaps_lever_primary = 1.0  # flaps: FULL
# sensors_state.levers_state.spoilers_lever = V_TRIState.UP
# sensors_state.levers_state.landing_gear_lever = V_TRIState.DOWN
# plane_commands = create_plane_commands(fjs_state, sensors_state)
# assert plane_commands.spoiler_right_deg == 0
# assert plane_commands.spoiler_left_deg == 0

# # spoilers: FULL - ground
# fjs_state.fjs_axes_state.flaps_lever_primary = 0.8  # flaps: RET
# sensors_state.levers_state.spoilers_lever = V_TRIState.UP
# sensors_state.levers_state.landing_gear_lever = V_TRIState.DOWN
# plane_commands = create_plane_commands(fjs_state, sensors_state)
# assert plane_commands.left_spoiler_deg == 50
# assert plane_commands.right_spoiler_deg == 50

# # spoilers: FULL - cruise
# fjs_state.fjs_axes_state.flaps_lever_primary = 0.8  # flaps: RET
# sensors_state.levers_state.spoilers_lever = V_TRIState.UP
# sensors_state.levers_state.landing_gear_lever = V_TRIState.UP
# plane_commands = create_plane_commands(fjs_state, sensors_state)
# assert plane_commands.left_spoiler_deg == 40
# assert plane_commands.right_spoiler_deg == 40

# # spoilers: HALF - landing
# fjs_state.fjs_axes_state.flaps_lever_primary = 0.8  # flaps: RET
# sensors_state.levers_state.spoilers_lever = V_TRIState.MID
# sensors_state.levers_state.landing_gear_lever = V_TRIState.DOWN
# plane_commands = create_plane_commands(fjs_state, sensors_state)
# assert plane_commands.left_spoiler_deg == 25
# assert plane_commands.right_spoiler_deg == 25

# # spoilers: HALF - cruise
# fjs_state.fjs_axes_state.flaps_lever_primary = 0.8  # flaps: RET
# sensors_state.levers_state.spoilers_lever = V_TRIState.MID
# sensors_state.levers_state.landing_gear_lever = V_TRIState.UP
# plane_commands = create_plane_commands(fjs_state, sensors_state)
# assert plane_commands.left_spoiler_deg == 20
# assert plane_commands.right_spoiler_deg == 20

# # spoilers: HALF - cruise - rolling right
# fjs_state.fjs_axes_state.flaps_lever_primary = 0.8  # flaps: RET
# fjs_state.fjs_axes_state.side_stick_x = 0.5  # rolling: right
# sensors_state.levers_state.spoilers_lever = V_TRIState.MID
# sensors_state.levers_state.landing_gear_lever = V_TRIState.UP
# plane_commands = create_plane_commands(fjs_state, sensors_state)
# assert plane_commands.left_spoiler_deg == 0
# assert plane_commands.right_spoiler_deg == 18

# # spoilers: HALF - cruise - rolling left
# fjs_state.fjs_axes_state.flaps_lever_primary = 0.8  # flaps: RET
# fjs_state.fjs_axes_state.side_stick_x = -0.5  # rolling: left
# sensors_state.levers_state.spoilers_lever = V_TRIState.MID
# sensors_state.levers_state.landing_gear_lever = V_TRIState.UP
# plane_commands = create_plane_commands(fjs_state, sensors_state)
# assert plane_commands.left_spoiler_deg == 18
# assert plane_commands.right_spoiler_deg == 0
