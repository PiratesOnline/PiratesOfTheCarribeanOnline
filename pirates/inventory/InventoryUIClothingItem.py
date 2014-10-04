# File: I (Python 2.4)

from direct.gui.DirectGui import *
from pandac.PandaModules import *
from pirates.piratesgui import PiratesGuiGlobals
from pirates.makeapirate import ClothingGlobals
from pirates.pirate import HumanDNA
from pirates.inventory import ItemGlobals
from pirates.inventory import ItemConstants
from pirates.uberdog.UberDogGlobals import InventoryType
from pirates.piratesbase import PLocalizer
from pirates.piratesbase import Freebooter
from pirates.inventory.ItemConstants import DYE_COLORS
from pirates.inventory import InventoryUIItem

class InventoryUIClothingItem(InventoryUIItem.InventoryUIItem):
    
    def __init__(self, manager, itemTuple, imageScaleFactor = 1.0):
        InventoryUIItem.InventoryUIItem.__init__(self, manager, itemTuple, imageScaleFactor = imageScaleFactor)
        self.initialiseoptions(InventoryUIClothingItem)
        self['relief'] = None
        tailorGui = loader.loadModel('models/gui/gui_icons_clothing')
        iconName = ItemGlobals.getIcon(itemTuple[1])
        self['image'] = tailorGui.find('**/%s' % iconName)
        self['image_scale'] = 0.10000000000000001 * imageScaleFactor
        iconColorIndex = ItemGlobals.getColor(itemTuple[1])
        dyeColor = itemTuple[3]
        if dyeColor:
            self.iconColor = (DYE_COLORS[dyeColor][0], DYE_COLORS[dyeColor][1], DYE_COLORS[dyeColor][2], 1.0)
        else:
            self.iconColor = (ItemConstants.COLOR_VALUES[iconColorIndex][0], ItemConstants.COLOR_VALUES[iconColorIndex][1], ItemConstants.COLOR_VALUES[iconColorIndex][2], 1.0)
        self['image_color'] = (self.iconColor[0], self.iconColor[1], self.iconColor[2], self.iconColor[3])
        self.helpFrame = None
        self.cm = CardMaker('itemCard')
        self.cm.setFrame(-0.29999999999999999, 0.29999999999999999, -0.089999999999999997, 0.089999999999999997)
        self.buffer = None
        self.lens = PerspectiveLens()
        self.lens.setNear(0.5)
        self.lens.setAspectRatio(0.59999999999999998 / 0.17999999999999999)
        self.realItem = None
        self.itemCard = None
        self.portraitSceneGraph = NodePath('PortraitSceneGraph')
        detailGui = loader.loadModel('models/gui/gui_card_detail')
        self.bg = detailGui.find('**/color')
        self.bg.setScale(4)
        self.bg.setPos(0, 17, -6.2999999999999998)
        self.glow = detailGui.find('**/glow')
        self.glow.setScale(3)
        self.glow.setPos(0, 17, -6.2999999999999998)
        self.glow.setColor(1, 1, 1, 0.80000000000000004)
        self.setBin('gui-fixed', 1)
        self.accept('open_main_window', self.createBuffer)
        self.accept('aspectRatioChanged', self.createBuffer)
        self.accept('close_main_window', self.destroyBuffer)
        self.displayHuman = self.manager.getDisplayHuman()
        self.masterHuman = self.manager.getMasterHuman()

    
    def destroy(self):
        self.displayHuman = None
        self.masterHuman = None
        if self.helpFrame:
            self.helpFrame.destroy()
            self.helpFrame = None
        
        self.destroyBuffer()
        if self.itemCard:
            self.itemCard.removeNode()
        
        if self.realItem:
            self.realItem.removeNode()
        
        InventoryUIItem.InventoryUIItem.destroy(self)

    
    def getName(self):
        itemTypeName = PLocalizer.getItemName(self.getId())
        clothingName = PLocalizer.TailorColorStrings.get(self.getColorId())
        if ItemGlobals.canDyeItem(self.getId()):
            return clothingName + ' ' + itemTypeName
        else:
            return itemTypeName

    
    def setColorId(self, colorId):
        self.itemTuple[3] = colorId

    
    def getColorId(self):
        return self.itemTuple[3]

    
    def getPlunderName(self):
        nameText = self.getName()
        titleColor = PiratesGuiGlobals.TextFG6
        rarity = ItemGlobals.getRarity(self.getId())
        if rarity == ItemGlobals.CRUDE:
            titleColor = PiratesGuiGlobals.TextFG24
        elif rarity == ItemGlobals.COMMON:
            titleColor = PiratesGuiGlobals.TextFG13
        elif rarity == ItemGlobals.RARE:
            titleColor = PiratesGuiGlobals.TextFG4
        elif rarity == ItemGlobals.FAMED:
            titleColor = PiratesGuiGlobals.TextFG5
        
        return (nameText, titleColor)

    
    def showDetails(self, cell, detailsPos, detailsHeight, event = None):
        self.notify.debug('Item showDetails')
        if self.manager.heldItem and self.manager.locked and cell.isEmpty() or not (self.itemTuple):
            self.notify.debug(' early exit')
            return None
        
        itemId = self.getId()
        self.helpFrame = DirectFrame(parent = self.manager, relief = None, state = DGG.DISABLED, sortOrder = 1)
        self.helpFrame.setBin('gui-popup', -5)
        detailGui = loader.loadModel('models/gui/gui_card_detail')
        topGui = loader.loadModel('models/gui/toplevel_gui')
        coinImage = topGui.find('**/treasure_w_coin*')
        halfWidth = 0.29999999999999999
        halfHeight = 0.20000000000000001
        basePosX = cell.getX(aspect2d)
        basePosZ = cell.getZ(aspect2d)
        cellSizeX = 0.0
        cellSizeZ = 0.0
        if cell:
            cellSizeX = cell.cellSizeX
            cellSizeZ = cell.cellSizeZ
        
        textScale = PiratesGuiGlobals.TextScaleMed
        titleScale = PiratesGuiGlobals.TextScaleTitleSmall
        if len(self.getName()) >= 30:
            titleNameScale = PiratesGuiGlobals.TextScaleLarge
        else:
            titleNameScale = PiratesGuiGlobals.TextScaleExtraLarge
        subtitleScale = PiratesGuiGlobals.TextScaleMed
        iconScalar = 1.5
        borderScaler = 0.25
        splitHeight = 0.01
        vMargin = 0.029999999999999999
        runningVertPosition = 0.29999999999999999
        runningSize = 0.0
        labels = []
        titleColor = PiratesGuiGlobals.TextFG6
        rarity = ItemGlobals.getRarity(itemId)
        rarityText = PLocalizer.getItemRarityName(rarity)
        typeText = ClothingGlobals.getClothingTypeName(ItemGlobals.getType(itemId))
        if rarity == ItemGlobals.CRUDE:
            titleColor = PiratesGuiGlobals.TextFG24
        elif rarity == ItemGlobals.COMMON:
            titleColor = PiratesGuiGlobals.TextFG13
        elif rarity == ItemGlobals.RARE:
            titleColor = PiratesGuiGlobals.TextFG4
        elif rarity == ItemGlobals.FAMED:
            titleColor = PiratesGuiGlobals.TextFG5
        
        titleLabel = DirectLabel(parent = self, relief = None, text = self.getName(), text_scale = titleNameScale, text_fg = titleColor, text_shadow = PiratesGuiGlobals.TextShadow, text_align = TextNode.ACenter, pos = (0.0, 0.0, runningVertPosition), text_pos = (0.0, -textScale))
        self.bg.setColor(titleColor)
        tHeight = 0.070000000000000007
        titleLabel.setZ(runningVertPosition)
        runningVertPosition -= tHeight
        runningSize += tHeight
        labels.append(titleLabel)
        subtitleLabel = DirectLabel(parent = self, relief = None, text = '\x1slant\x1%s %s\x2' % (rarityText, typeText), text_scale = subtitleScale, text_fg = PiratesGuiGlobals.TextFG2, text_shadow = PiratesGuiGlobals.TextShadow, text_align = TextNode.ACenter, pos = (0.0, 0.0, runningVertPosition), text_pos = (0.0, -textScale))
        subtHeight = 0.050000000000000003
        subtitleLabel.setZ(subtHeight * 0.5 + runningVertPosition)
        runningVertPosition -= subtHeight
        runningSize += subtHeight
        labels.append(subtitleLabel)
        clothingType = ItemGlobals.getType(itemId)
        if localAvatar.style.getGender() == 'm':
            maleModelId = ItemGlobals.getMaleModelId(itemId)
            if maleModelId != -1:
                modelId = maleModelId
                texId = ItemGlobals.getMaleTextureId(itemId)
                dna = HumanDNA.HumanDNA(localAvatar.style.gender)
                dna.copy(localAvatar.style)
                gender = 'm'
            else:
                modelId = ItemGlobals.getFemaleModelId(itemId)
                texId = ItemGlobals.getFemaleTextureId(itemId)
                dna = HumanDNA.HumanDNA('f')
                gender = 'f'
        else:
            femaleModelId = ItemGlobals.getFemaleModelId(itemId)
            if femaleModelId != -1:
                modelId = femaleModelId
                texId = ItemGlobals.getFemaleTextureId(itemId)
                dna = HumanDNA.HumanDNA(localAvatar.style.gender)
                dna.copy(localAvatar.style)
                gender = 'f'
            else:
                modelId = ItemGlobals.getMaleModelId(itemId)
                texId = ItemGlobals.getMaleTextureId(itemId)
                dna = HumanDNA.HumanDNA('m')
                gender = 'm'
        bodyShape = localAvatar.style.getBodyShape()
        bodyHeight = localAvatar.style.getBodyHeight()
        bodyOffset = 0.5
        headOffset = 0
        topOffset = 0
        pantOffset = 0
        beltOffset = 0
        shoeOffset = 0
        if bodyShape == 0:
            bodyOffset = 1
            headOffset = 0.69999999999999996
            topOffset = 0.69999999999999996
            pantOffset = 0.20000000000000001
            beltOffset = 0.5
        elif bodyShape == 1:
            bodyOffset = 0
            if gender == 'm':
                headOffset = -0.10000000000000001
                beltOffset = 0.10000000000000001
                shoeOffset = 0.10000000000000001
            elif gender == 'f':
                headOffset = 0.59999999999999998
                topOffset = 0.40000000000000002
                beltOffset = 0.40000000000000002
                shoeOffset = 0.10000000000000001
            
        elif bodyShape == 2:
            bodyOffset = 0.5
        elif bodyShape == 3:
            bodyOffset = 1
            if gender == 'm':
                topOffset = 0.10000000000000001
                beltOffset = 0.10000000000000001
            elif gender == 'f':
                headOffset = -0.40000000000000002
                topOffset = -0.10000000000000001
                beltOffset = -0.10000000000000001
                pantOffset = -0.10000000000000001
            
        elif bodyShape == 4:
            bodyOffset = 0.5
            if gender == 'm':
                headOffset = -0.20000000000000001
                topOffset = -0.29999999999999999
            elif gender == 'f':
                headOffset = 0.10000000000000001
                beltOffset = 0.10000000000000001
            
        elif bodyShape == 5:
            bodyOffset = 0.5
        elif bodyShape == 6:
            bodyOffset = 0.5
            if gender == 'f':
                headOffset = 0.40000000000000002
                topOffset = 0.40000000000000002
                beltOffset = 0.29999999999999999
            
        elif bodyShape == 7:
            bodyOffset = 0.5
        elif bodyShape == 8:
            bodyOffset = 0.5
            headOffset = -0.20000000000000001
            topOffset = -0.20000000000000001
        elif bodyShape == 9:
            bodyOffset = 0.5
            headOffset = -0.20000000000000001
            topOffset = -0.20000000000000001
        
        m = Mat4(Mat4.identMat())
        topColor = localAvatar.style.getClothesBotColor()
        botColor = localAvatar.style.getClothesTopColor()
        hatColor = localAvatar.style.getHatColor()
        (shirtIdx, shirtTex) = localAvatar.style.getClothesShirt()
        (hatIdx, hatTex) = localAvatar.style.getClothesHat()
        (coatIdx, coatTex) = localAvatar.style.getClothesCoat()
        (beltIdx, beltTex) = localAvatar.style.getClothesBelt()
        (shoeIdx, shoeTex) = localAvatar.style.getClothesShoe()
        (vestIdx, vestTex) = localAvatar.style.getClothesVest()
        (pantIdx, pantTex) = localAvatar.style.getClothesPant()
        dna.setClothesBotColor(topColor[0], topColor[1], topColor[2])
        dna.setClothesTopColor(botColor[0], botColor[1], botColor[2])
        dna.setHatColor(hatColor)
        dna.setClothesShirt(shirtIdx, shirtTex)
        dna.setClothesHat(hatIdx, hatTex)
        dna.setClothesBelt(beltIdx, beltTex)
        dna.setClothesPant(pantIdx, pantTex)
        dna.setClothesShoe(shoeIdx, shoeTex)
        if clothingType == ClothingGlobals.SHIRT:
            dna.setClothesVest(0)
            dna.setClothesCoat(0)
        elif clothingType == ClothingGlobals.VEST:
            dna.setClothesCoat(0)
        elif clothingType == ClothingGlobals.BELT:
            dna.setClothesCoat(0)
            dna.setClothesVest(0)
        else:
            dna.setClothesVest(vestIdx, vestTex)
            dna.setClothesCoat(coatIdx, coatTex)
        dna.setClothesByType(ClothingGlobals.CLOTHING_STRING[clothingType], modelId, texId, self.itemTuple[3])
        self.displayHuman.setDNAString(dna)
        self.displayHuman.generateHuman(gender, self.masterHuman)
        self.displayHuman.stopBlink()
        self.displayHuman.pose('idle', 1)
        lodNode = self.displayHuman.find('**/+LODNode').node()
        lodNode.forceSwitch(lodNode.getHighestSwitch())
        if clothingType == ClothingGlobals.HAT:
            self.displayHuman.getLOD('2000').getChild(0).node().findJoint('def_head01').getNetTransform(m)
            headHeight = TransformState.makeMat(m).getPos().getZ()
            offsetZ = (-headHeight - 0.40000000000000002) + headOffset - bodyHeight * 1.0
            offsetY = 2.0 + bodyOffset
            offsetH = 200
        elif clothingType == ClothingGlobals.SHIRT:
            self.displayHuman.getLOD('2000').getChild(0).node().findJoint('def_spine03').getNetTransform(m)
            spine3Height = TransformState.makeMat(m).getPos().getZ()
            offsetZ = -spine3Height + topOffset - bodyHeight * 1.3999999999999999
            offsetY = 3.25 + bodyOffset
            offsetH = 200
        elif clothingType == ClothingGlobals.VEST:
            self.displayHuman.getLOD('2000').getChild(0).node().findJoint('def_spine03').getNetTransform(m)
            spine3Height = TransformState.makeMat(m).getPos().getZ()
            offsetZ = -spine3Height + topOffset - bodyHeight * 1.3999999999999999
            offsetY = 3.5 + bodyOffset
            offsetH = 200
        elif clothingType == ClothingGlobals.COAT:
            self.displayHuman.getLOD('2000').getChild(0).node().findJoint('def_spine02').getNetTransform(m)
            spine2Height = TransformState.makeMat(m).getPos().getZ()
            offsetZ = -spine2Height + topOffset - bodyHeight * 1.3999999999999999
            offsetY = 4.5 + bodyOffset
            offsetH = 200
        elif clothingType == ClothingGlobals.PANT:
            self.displayHuman.getLOD('2000').getChild(0).node().findJoint('def_right_knee').getNetTransform(m)
            kneeHeight = TransformState.makeMat(m).getPos().getZ()
            offsetZ = -kneeHeight + pantOffset - 0.5 - bodyHeight * 0.29999999999999999
            offsetY = 4.5 + bodyOffset
            offsetH = 200
        elif clothingType == ClothingGlobals.BELT:
            self.displayHuman.getLOD('2000').getChild(0).node().findJoint('def_hips').getNetTransform(m)
            hipHeight = TransformState.makeMat(m).getPos().getZ()
            offsetZ = -hipHeight + beltOffset - bodyHeight * 0.5
            offsetY = 1.7 + bodyOffset
            offsetH = 180
        elif clothingType == ClothingGlobals.SHOE:
            self.displayHuman.getLOD('2000').getChild(0).node().findJoint('def_right_ankle').getNetTransform(m)
            ankleHeight = TransformState.makeMat(m).getPos().getZ()
            offsetZ = -ankleHeight + shoeOffset - 0.14999999999999999 - bodyHeight * -0.10000000000000001
            offsetY = 3.25 + bodyOffset
            offsetH = 200
        else:
            offsetZ = 0
            offsetY = 0
            offsetH = 0
        offsetX = 0
        self.displayHuman.setY(offsetY)
        self.displayHuman.setZ(offsetZ)
        self.displayHuman.setX(offsetX)
        self.displayHuman.setH(offsetH)
        self.displayHuman.reparentTo(self.portraitSceneGraph)
        iHeight = 0.17999999999999999
        self.createBuffer()
        self.itemCard.setZ(runningVertPosition - 0.059999999999999998)
        runningVertPosition -= iHeight
        runningSize += iHeight
        labels.append(self.itemCard)
        if self.showResaleValue:
            value = int(ItemGlobals.getGoldCost(itemId) * ItemGlobals.GOLD_SALE_MULTIPLIER)
        else:
            value = ItemGlobals.getGoldCost(itemId)
        goldLabel = DirectLabel(parent = self, relief = None, image = coinImage, image_scale = 0.12, image_pos = Vec3(0.025000000000000001, 0, -0.02), text = str(value), text_scale = subtitleScale, text_align = TextNode.ARight, text_fg = PiratesGuiGlobals.TextFG1, text_shadow = PiratesGuiGlobals.TextShadow, pos = (halfWidth - 0.050000000000000003, 0.0, runningVertPosition + 0.080000000000000002), text_pos = (0.0, -textScale))
        labels.append(goldLabel)
        descriptionLabel = DirectLabel(parent = self, relief = None, text = PLocalizer.getItemFlavorText(itemId), text_scale = textScale, text_wordwrap = halfWidth * 2.0 * (0.94999999999999996 / textScale), text_fg = PiratesGuiGlobals.TextFG0, text_align = TextNode.ALeft, pos = (-halfWidth + textScale * 0.5, 0.0, runningVertPosition), text_pos = (0.0, -textScale))
        dHeight = descriptionLabel.getHeight() + 0.02
        runningVertPosition -= dHeight
        runningSize += dHeight
        labels.append(descriptionLabel)
        if not Freebooter.getPaidStatus(localAvatar.getDoId()):
            if rarity != ItemGlobals.CRUDE:
                unlimitedLabel = DirectLabel(parent = self, relief = None, text = PLocalizer.UnlimitedAccessRequirement, text_scale = textScale, text_wordwrap = halfWidth * 2.0 * (1.5 / titleScale), text_fg = PiratesGuiGlobals.TextFG6, text_shadow = PiratesGuiGlobals.TextShadow, text_align = TextNode.ACenter, pos = (0.0, 0.0, runningVertPosition), text_pos = (0.0, -textScale))
                uHeight = unlimitedLabel.getHeight()
                runningVertPosition -= uHeight
                runningSize += uHeight
                labels.append(unlimitedLabel)
            
        
        runningVertPosition -= 0.02
        runningSize += 0.02
        panels = self.helpFrame.attachNewNode('panels')
        topPanel = panels.attachNewNode('middlePanel')
        detailGui.find('**/top_panel').copyTo(topPanel)
        topPanel.setScale(0.080000000000000002)
        topPanel.reparentTo(self.helpFrame)
        middlePanel = panels.attachNewNode('middlePanel')
        detailGui.find('**/middle_panel').copyTo(middlePanel)
        middlePanel.setScale(0.080000000000000002)
        middlePanel.reparentTo(self.helpFrame)
        placement = 0
        i = 0
        heightMax = -0.080000000000000002
        currentHeight = runningVertPosition
        if detailsHeight:
            currentHeight = -detailsHeight
        
        while currentHeight < heightMax:
            middlePanel = panels.attachNewNode('middlePanel%s' % 1)
            detailGui.find('**/middle_panel').copyTo(middlePanel)
            middlePanel.setScale(0.080000000000000002)
            middlePanel.reparentTo(self.helpFrame)
            if currentHeight + 0.20000000000000001 >= heightMax:
                difference = heightMax - currentHeight
                placement += (0.16800000000000001 / 0.20000000000000001) * difference
                currentHeight += difference
            else:
                placement += 0.16800000000000001
                currentHeight += 0.20000000000000001
            middlePanel.setZ(-placement)
            i += 1
        bottomPanel = panels.attachNewNode('bottomPanel')
        detailGui.find('**/bottom_panel').copyTo(bottomPanel)
        bottomPanel.setScale(0.080000000000000002)
        bottomPanel.setZ(-placement)
        bottomPanel.reparentTo(self.helpFrame)
        colorPanel = self.helpFrame.attachNewNode('colorPanel')
        detailGui.find('**/color').copyTo(colorPanel)
        colorPanel.setScale(0.080000000000000002)
        colorPanel.setColor(titleColor)
        colorPanel.reparentTo(self.helpFrame)
        lineBreakTopPanel = panels.attachNewNode('lineBreakTopPanel')
        detailGui.find('**/line_break_top').copyTo(lineBreakTopPanel)
        lineBreakTopPanel.setScale(0.080000000000000002, 0.080000000000000002, 0.070000000000000007)
        lineBreakTopPanel.setZ(0.0080000000000000002)
        lineBreakTopPanel.reparentTo(self.helpFrame)
        panels.flattenStrong()
        self.helpFrame['frameSize'] = (-halfWidth, halfWidth, -(runningSize + vMargin), vMargin)
        totalHeight = self.helpFrame.getHeight() - 0.10000000000000001
        for label in labels:
            label.reparentTo(self.helpFrame)
        
        if basePosX > 0.0:
            newPosX = basePosX - halfWidth + cellSizeX * 0.45000000000000001
        else:
            newPosX = basePosX + halfWidth + cellSizeX * 0.45000000000000001
        if basePosZ > 0.0:
            newPosZ = basePosZ + cellSizeZ * 0.45000000000000001
        else:
            newPosZ = basePosZ + totalHeight - cellSizeZ * 0.75
        if detailsPos:
            (newPosX, newPosZ) = detailsPos
        
        self.helpFrame.setPos(newPosX, 0, newPosZ)

    
    def hideDetails(self, event = None):
        InventoryUIItem.InventoryUIItem.hideDetails(self, event)
        if self.helpFrame:
            self.helpFrame.destroy()
            self.helpFrame = None
        
        self.destroyBuffer()
        if self.realItem:
            self.realItem.removeNode()
        
        if self.displayHuman:
            self.displayHuman.detachNode()
        

    
    def createBuffer(self):
        self.destroyBuffer()
        self.buffer = base.win.makeTextureBuffer('par', 256, 256)
        self.buffer.setOneShot(True)
        self.cam = base.makeCamera(win = self.buffer, scene = self.portraitSceneGraph, clearColor = Vec4(1), lens = self.lens)
        self.cam.node().getDisplayRegion(0).setIncompleteRender(False)
        self.cam.reparentTo(self.portraitSceneGraph)
        self.bg.reparentTo(self.cam)
        self.glow.reparentTo(self.cam)
        if self.itemCard:
            self.itemCard.removeNode()
        
        tex = self.buffer.getTexture()
        self.itemCard = NodePath(self.cm.generate())
        self.itemCard.setTexture(tex, 1)
        if self.helpFrame:
            self.itemCard.reparentTo(self.helpFrame)
        

    
    def destroyBuffer(self):
        if self.buffer:
            base.graphicsEngine.removeWindow(self.buffer)
            self.buffer = None
            self.bg.detachNode()
            self.glow.detachNode()
            self.cam.removeNode()
            self.cam = None
        


