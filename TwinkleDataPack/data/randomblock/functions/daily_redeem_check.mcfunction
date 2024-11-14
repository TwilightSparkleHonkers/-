# Check each player if they can redeem a block
execute as @a[scores={redeem_timer=0..}] run function randomblock:give_random_block

# Increment the redeem_timer for players who have redeemed
scoreboard players add @a[scores={redeem_timer=1..}] redeem_timer 1

# Reset the timer after 24 hours (1,728,000 ticks)
scoreboard players reset @a[scores={redeem_timer=1728000..}] redeem_timer
