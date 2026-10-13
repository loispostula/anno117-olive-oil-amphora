-- Development only: one-time gift of press inputs, so the Olive Press can run without its supply chains.
-- Same API as the game's infinite-material-ubi mod. Gives once per game launch, on the first owned island
-- you look at; stock is not refilled, so the warehouse counts show what the press consumes.

local TestUnlock = {}

local gifts = { [2072] = 30, [31700] = 10 } -- Olives, Amphorae
local given = false

function TestUnlock.Tick()
    if given then return end
    local area = Area.Current
    if area and area.AreaOwnerIsCurrentParticipant then
        for product, amount in pairs(gifts) do
            local room = area.Economy:GetStorageCapacity(product) - area.Economy:GetStorageAmount(product)
            if room > 0 then
                area.Economy:AddAmount(product, math.min(amount, room))
            end
        end
        given = true
    end
end

return TestUnlock;
