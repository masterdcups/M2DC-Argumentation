<?xml version="1.0" ?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <!-- Output to text (csv) -->
  <xsl:output method="text"/>

  <!-- Root -->
  <xsl:template match="/">
    <!-- Name -->
    <xsl:apply-templates select="//h2" />
    <!-- Pros -->
    <xsl:apply-templates mode="pro" select="//div[@class='columns-container']/div[2]/*/div[1]//a" />
    <!-- Cons -->
    <xsl:apply-templates mode="con" select="//div[@class='columns-container']/div[2]/*/div[2]//a" />
  </xsl:template>

  <!-- Name -->
  <xsl:template match="h2" >
    <xsl:text>#name: </xsl:text>
    <xsl:value-of select="." />
    <xsl:text>&#xa;</xsl:text> <!-- newline -->    
  </xsl:template>
    
  <!-- Links to debates (pros) -->
  <xsl:template mode="pro" match="a">
    <xsl:value-of select="@href" />
    <xsl:text>;</xsl:text>
    <xsl:value-of select=".//h3" />
    <xsl:text>;1</xsl:text>
    <xsl:text>&#xa;</xsl:text> <!-- newline -->
  </xsl:template>

  <!-- Links to debates (cons) -->
  <xsl:template mode="con" match="a">
    <xsl:value-of select="@href" />
    <xsl:text>;</xsl:text>
    <xsl:value-of select=".//h3" />
    <xsl:text>;-1</xsl:text>
    <xsl:text>&#xa;</xsl:text> <!-- newline -->
  </xsl:template>
  
</xsl:stylesheet>
